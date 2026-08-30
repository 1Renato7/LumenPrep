"""Derive and persist current Incidents after a terminal canonical event.

The pipeline consumes only persisted aggregate windows and detector candidates.
It deliberately does not consult memory, prompt an LLM, or turn an RCA hypothesis
into a supported cause.  Memory/explanation remain read-time enrichment of the
already-persisted current Incident.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, TypeAlias

from app.agent import DiagnosticAgentService
from app.aggregation import WindowMetrics, compute_payment_conversion_observations, compute_windows
from app.detection import detect_candidates, detect_payment_conversion_candidates
from app.incidents import DuckDBIncidentRepository, Evidence, Impact, Incident, RootCause, correlate_candidates, compute_impact, to_incident
from app.rca import explore_slices, rank_hypotheses

logger = logging.getLogger(__name__)

LOW_SAMPLE_ATTEMPTS = 12
MINIMUM_UNIQUE_PAYMENTS = 10
HOMOGENEOUS_FAILURE_MINIMUM = 12
# Outcome sentinels of the decline profile: they describe the healthy or
# unmapped part of a window, not a refusal anyone can be routed to.
DECLINE_PROFILE_SENTINELS = frozenset({"NO_DECLINE", "NOT_APPLICABLE", "UNMAPPED_DECLINE"})
SuggestionJob: TypeAlias = tuple[Incident, dict[str, int], list[dict[str, Any]]]


def derive_incidents_for_correlation(
    con, correlation_id: str, *, suggestion_jobs: list[SuggestionJob] | None = None
) -> list[str]:
    """Persist newly observed Incident groups and return their stable IDs.

    Detector history may contain other correlations, but only candidates produced
    for the just-processed correlation may create or update its Incidents.
    """
    # A public batch is one correlation. Wait until it is terminal so a burst
    # rule can inspect the whole submitted set instead of an arbitrary worker
    # prefix. Direct event-ingestion callers have no transaction rows and keep
    # the existing immediate detector behavior.
    if not _correlation_is_terminal(con, correlation_id):
        return []

    repository = DuckDBIncidentRepository()
    homogeneous = _homogeneous_failure_incident(con, correlation_id)
    if homogeneous is not None:
        incident, decline_profile, refusal_summaries = homogeneous
        persisted, created = repository.upsert_with_status(incident)
        if created:
            repository.create_notification(persisted.incident_id)
        _link_matching_transactions(
            con, repository, persisted.model_dump(mode="json"), allow_inconclusive=True
        )
        if suggestion_jobs is None:
            _suggest_for_persisted_incident(persisted, decline_profile, refusal_summaries)
        else:
            suggestion_jobs.append((persisted, decline_profile, refusal_summaries))
        return [persisted.incident_id]

    windows = compute_windows(con)
    conversion_windows = compute_payment_conversion_observations(con)
    candidates = [
        candidate
        for candidate in detect_candidates(windows, low_sample_attempts=LOW_SAMPLE_ATTEMPTS)
        if candidate.correlation_id == correlation_id and candidate.slice
    ]
    candidates.extend(
        candidate for candidate in detect_payment_conversion_candidates(
            conversion_windows, minimum_unique_payments=MINIMUM_UNIQUE_PAYMENTS
        ) if candidate.correlation_id == correlation_id and candidate.slice
    )
    if not candidates:
        return []

    incident_ids: list[str] = []
    for group in correlate_candidates(_most_specific_candidates(candidates)):
        window = _window_for_group(windows + conversion_windows, group.correlation_id, group.candidates[0])
        if window is None:
            continue
        ranking = rank_hypotheses(explore_slices(group.candidates, min_support=LOW_SAMPLE_ATTEMPTS))
        root_cause = ranking.to_root_cause(allow_supported=True)
        if root_cause.status == "SUPPORTED":
            root_cause = root_cause.model_copy(update={"category": _category_from_decline_profile(window.decline_profile, root_cause.category)})
        incident = to_incident(
            group,
            compute_impact(group, window),
            root_cause,
            incident_id=_incident_id(group.correlation_id, window, group.scope),
            title=_title(group.scope),
            evidence=_evidence(group.candidates, window.decline_profile),
            recommendations=[],
            limitations=(
                () if root_cause.status == "SUPPORTED" else
                ("Evidence is insufficient to name a specific cause; investigate the ranked alternatives.",)
            ),
            decline_codes=_memory_decline_codes(window.decline_profile),
        )
        persisted, created = repository.upsert_with_status(incident)
        if created:
            repository.create_notification(persisted.incident_id)
        _link_matching_transactions(con, repository, persisted.model_dump(mode="json"))
        summaries = _refusal_code_summaries(con, persisted.model_dump(mode="json"))
        if suggestion_jobs is None:
            _suggest_for_persisted_incident(persisted, window.decline_profile, summaries)
        else:
            suggestion_jobs.append((persisted, dict(window.decline_profile), summaries))
        incident_ids.append(persisted.incident_id)
    return incident_ids


def _correlation_is_terminal(con, correlation_id: str) -> bool:
    row = con.execute(
        """SELECT count(*), sum(CASE WHEN status = 'PROCESSING' THEN 1 ELSE 0 END)
           FROM transaction_records WHERE correlation_id = ?""",
        [correlation_id],
    ).fetchone()
    return not row or int(row[0]) == 0 or int(row[1] or 0) == 0


def _homogeneous_failure_incident(
    con, correlation_id: str
) -> tuple[Incident, dict[str, int], list[dict[str, Any]]] | None:
    """Build an operational Incident for one terminal, mapped-refusal burst.

    A provider response code identifies the common observed symptom, not the
    variable that caused it. This path is therefore intentionally
    ``INCONCLUSIVE`` even when the catalog can normalize the code.
    """
    rows = con.execute(
        """SELECT created_at, input_json, classification_json, outcome_json
           FROM transaction_records WHERE correlation_id = ?
           ORDER BY transaction_id""",
        [correlation_id],
    ).fetchall()
    if len(rows) < HOMOGENEOUS_FAILURE_MINIMUM:
        return None

    signatures: set[tuple[str, str, tuple[tuple[str, str], ...]]] = set()
    total_amount = 0
    observed_at: datetime | None = None
    resolution: dict[str, Any] | None = None
    for created_at, input_json, classification_json, outcome_json in rows:
        if not classification_json or not outcome_json:
            return None
        classification = json.loads(classification_json)
        outcome = json.loads(outcome_json)
        mapped = classification.get("refusal_resolution")
        if (
            not isinstance(mapped, dict)
            or mapped.get("lookup_status") != "MATCH_FOUND"
            or mapped.get("outcome") != "FAILED"
            or outcome.get("result") != "FAILED"
        ):
            return None
        transaction_input = json.loads(input_json)
        scope = _homogeneous_scope(transaction_input)
        response_code = str(mapped.get("response_code") or "")
        normalized_code = str(mapped.get("normalized_code") or "")
        if not response_code or not normalized_code:
            return None
        signatures.add((response_code, normalized_code, tuple(sorted(scope.items()))))
        total_amount += int(transaction_input["amount_minor"])
        event_time = created_at if isinstance(created_at, datetime) else datetime.fromisoformat(str(created_at))
        observed_at = event_time if observed_at is None or event_time < observed_at else observed_at
        resolution = mapped

    if len(signatures) != 1 or observed_at is None or resolution is None:
        return None
    response_code, normalized_code, scope_items = signatures.pop()
    scope = {key: [value] for key, value in scope_items}
    start = _iso_z(observed_at)
    end = _iso_z(observed_at + timedelta(minutes=1))
    candidate_id = sha256(
        f"{correlation_id}|{response_code}|{json.dumps(scope, sort_keys=True)}".encode("utf-8")
    ).hexdigest()[:16]
    candidate = {
        "candidate_id": f"homogeneous_{candidate_id}",
        "correlation_id": correlation_id,
        "slice": {key: values[0] for key, values in scope.items()},
        "metric": "HOMOGENEOUS_FAILURE_BURST",
        "window": {"start": start, "end": end},
        "observed": 1.0,
        "expected": None,
        "sample_size": len(rows),
        "lost_approvals": len(rows),
        "statistical_strength": 1.0,
        "loss_coverage": 1.0,
        "evidence_refs": [f"correlation://{correlation_id}/response-code/{response_code}"],
    }
    group = correlate_candidates([candidate])[0]
    evidence_id = f"evd_homogeneous_{candidate_id}"
    root_cause = RootCause(
        status="INCONCLUSIVE",
        category=None,
        confidence=0.0,
        confidence_factors={"homogeneous_failure": 1.0, "causal_variation": 0.0},
        alternatives=[],
    )
    incident = to_incident(
        group,
        Impact(amount_minor=total_amount, currency=scope["currency"][0]),
        root_cause,
        incident_id=f"inc_homogeneous_{candidate_id}",
        title=f"Homogeneous mapped refusal burst for {_title(scope).removeprefix('Payment degradation for ')}",
        evidence=[Evidence(
            evidence_id=evidence_id,
            kind="HOMOGENEOUS_MAPPED_REFUSAL",
            statement=(
                f"{len(rows)} terminal transactions in this correlation share mapped response code "
                f"{response_code} ({normalized_code}) and the same diagnosis scope."
            ),
            source_ref=f"correlation://{correlation_id}/response-code/{response_code}",
        )],
        recommendations=[],
        limitations=(
            "All observed failures have the same mapped response and scope; the data cannot identify a root-cause variable.",
        ),
        detected_at=end,
        estimated_started_at=start,
        decline_codes=[normalized_code],
    )
    return incident, {normalized_code: len(rows)}, [{
        "provider_id": str(resolution["provider_id"]),
        "issuer_bank": str(resolution["issuer_bank"]),
        "card_brand": str(resolution["card_brand"]),
        "response_code": response_code,
        "normalized_code": normalized_code,
        "reason": str(resolution.get("reason") or "Mapped provider refusal"),
        "source": str(resolution.get("source") or "UNKNOWN"),
        "mapping_version": str(resolution.get("mapping_version") or "UNKNOWN"),
        "transaction_count": len(rows),
        "evidence_id": evidence_id,
    }]


def _homogeneous_scope(transaction_input: dict[str, Any]) -> dict[str, str]:
    return {
        "merchant_id": str(transaction_input["merchant_id"]),
        "provider_id": str(transaction_input["provider_id"]),
        "payment_method_category": str(transaction_input["payment_method_category"]),
        "country": str(transaction_input["country"]),
        "issuer_bank_id": str(transaction_input["issuer_bank"]),
        "currency": str(transaction_input["currency"]),
    }


def _iso_z(value: datetime) -> str:
    return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _suggest_for_persisted_incident(
    incident: Incident,
    decline_profile: dict[str, int],
    refusal_code_summaries: list[dict[str, Any]] | None = None,
) -> None:
    """Run the proactive agent on an Incident that is already durable.

    This call is deliberately last and deliberately swallowed. The transaction
    worker schedules it only after committing and releasing its DuckDB lock, so
    a slow or unavailable model never holds the transaction lifecycle open.
    Detection, the Incident and the deterministic explanation survive a model
    that is slow, unavailable or wrong.
    """
    try:
        DiagnosticAgentService().suggest_for_incident(
            incident,
            decline_profile=decline_profile,
            refusal_code_summaries=refusal_code_summaries or [],
        )
    except Exception as error:
        logger.warning(
            "diagnostic agent skipped for %s: %s", incident.incident_id, type(error).__name__
        )


def _most_specific_candidates(candidates: list[Any]) -> list[Any]:
    """Create incidents from the deepest observed slices only.

    The cube also emits parent rollups so RCA can compare contributions. Turning
    every parent into an Incident would duplicate a single degradation dozens of
    times. Leaves preserve genuinely separate intersections for the next pass.
    """
    def depth(candidate: Any) -> int:
        slice_values = candidate.slice if hasattr(candidate, "slice") else candidate["slice"]
        return len([key for key in slice_values if key != "currency"])

    max_depth = max((depth(candidate) for candidate in candidates), default=0)
    return [candidate for candidate in candidates if depth(candidate) == max_depth]


def _window_for_group(windows: list[WindowMetrics], correlation_id: str, candidate: dict[str, Any]) -> WindowMetrics | None:
    target = candidate.get("window", {})
    for window in windows:
        if (
            window.correlation_id == correlation_id
            and window.window_start == target.get("start")
            and window.window_end == target.get("end")
            and window.dimensions == candidate.get("slice")
        ):
            return window
    return None


def _incident_id(correlation_id: str, window: WindowMetrics, scope: dict[str, list[str]]) -> str:
    payload = json.dumps(
        {
            "correlation_id": correlation_id,
            "window_start": window.window_start,
            "window_end": window.window_end,
            "scope": scope,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"inc_{sha256(payload.encode('utf-8')).hexdigest()[:20]}"


def _title(scope: dict[str, list[str]]) -> str:
    label = ", ".join(f"{key}={','.join(values)}" for key, values in sorted(scope.items()))
    return f"Payment degradation for {label}"


def _evidence(candidates: tuple[dict[str, Any], ...], decline_profile: dict[str, int]) -> list[Evidence]:
    values: list[Evidence] = []
    for candidate in candidates:
        for source_ref in candidate.get("evidence_refs", []):
            source = str(source_ref)
            digest = sha256(f"{candidate['candidate_id']}:{source}".encode("utf-8")).hexdigest()[:16]
            values.append(
                Evidence(
                    evidence_id=f"evd_det_{digest}",
                    kind="DETECTOR_CANDIDATE",
                    statement=f"Detector candidate {candidate['candidate_id']} contributed to this Incident.",
                    source_ref=source,
                )
            )
        if candidate.get("metric") == "PAYMENT_CONVERSION":
            values.append(Evidence(
                evidence_id=f"evd_conversion_{candidate['candidate_id']}", kind="PAYMENT_CONVERSION",
                statement=(f"Payment conversion was {candidate['observed']:.1%} against a historical {candidate['expected']:.1%} "
                           f"baseline across {candidate['sample_size']} unique payments in the closed 60-minute observation."),
                source_ref=f"conversion://{candidate['window']['start']}/{candidate['window']['end']}",
            ))
    if decline_profile:
        dominant, count = max(decline_profile.items(), key=lambda item: item[1])
        values.append(
            Evidence(
                evidence_id=f"evd_decline_{sha256(dominant.encode('utf-8')).hexdigest()[:16]}",
                kind="DECLINE_PROFILE",
                statement=f"Dominant decline profile is {dominant} across {count} eligible attempts in this slice.",
                source_ref="window://decline-profile",
            )
        )
    return list({item.evidence_id: item for item in values}.values())


def _memory_decline_codes(profile: dict[str, int]) -> list[str]:
    """Expose observed normalized decline codes to structured memory retrieval."""
    return sorted(
        code
        for code, count in profile.items()
        if count > 0 and code not in {"NO_DECLINE", "UNMAPPED_DECLINE"}
    )


def _category_from_decline_profile(profile: dict[str, int], fallback: str | None) -> str:
    """Derive the category from the leading *decline*, never from the sentinels.

    ``NO_DECLINE`` counts the approvals of the window and ``NOT_APPLICABLE``
    counts methods that have no issuer decline at all. Leaving either in the
    argmax lets the healthy majority of a degraded window pick the category: a
    window that fell to 63% approval still has more approvals than refusals, so
    the sentinel wins, the function falls through to ``fallback`` and this
    override silently never fires. The same exclusion already guards
    ``app.agent.llm._dominant_decline``.
    """
    declines = {
        code: count
        for code, count in profile.items()
        if count > 0 and code not in DECLINE_PROFILE_SENTINELS
    }
    if not declines:
        return fallback or "UNCLASSIFIED_DEGRADATION"
    # The code breaks ties so the same profile always yields the same category.
    code = max(declines.items(), key=lambda item: (item[1], item[0]))[0]
    if code.startswith("PROVIDER_"):
        return "PROVIDER_DEGRADATION"
    if code.startswith("ISSUER_") or code in {"DO_NOT_HONOR", "INSUFFICIENT_FUNDS", "TRANSACTION_NOT_PERMITTED"}:
        return "ISSUER_OUTAGE"
    if code in {"METHOD_UNAVAILABLE", "CASH_IN_STORE_UNAVAILABLE"}:
        return "PAYMENT_METHOD_DEGRADATION"
    return fallback or "UNCLASSIFIED_DEGRADATION"


def _link_matching_transactions(
    con, repository: DuckDBIncidentRepository, incident: dict[str, Any], *, allow_inconclusive: bool = False
) -> None:
    """Link authorized transactions with matching correlation, scope and evidence.

    Ordinary INCONCLUSIVE detector groups stay unlinked so a hypothesis never
    reads as a confirmed recurrence. The explicit homogeneous-burst path may
    opt in: it records a scoped operational association, while preserving the
    Incident's INCONCLUSIVE causal status.
    """
    if incident.get("state") != "SUPPORTED" and not (
        allow_inconclusive and incident.get("state") == "INCONCLUSIVE"
    ):
        return
    rows = con.execute(
        "SELECT transaction_id, input_json, classification_json, correlation_id FROM transaction_records WHERE correlation_id = ?",
        [incident["correlation_id"]],
    ).fetchall()
    scope = incident["scope"]
    for transaction_id, input_json, classification_json, correlation_id in rows:
        if not classification_json:
            continue
        transaction_input = json.loads(input_json)
        if not _input_matches_scope(transaction_input, scope):
            continue
        classification = json.loads(classification_json)
        evidence_ids = classification.get("evidence_ids", [])
        if not isinstance(evidence_ids, list) or not evidence_ids:
            continue
        repository.link_transaction(
            transaction_id,
            incident["incident_id"],
            evidence_ids=[str(item) for item in evidence_ids],
            correlation_id=correlation_id,
        )
        related = [item for item in classification.get("related_incident_ids", []) if isinstance(item, str)]
        is_new_link = incident["incident_id"] not in related
        if is_new_link:
            related.append(incident["incident_id"])
            classification["related_incident_ids"] = sorted(related)
            existing_recurrences = classification.get("related_incidents", [])
            retained = [
                item for item in existing_recurrences
                if isinstance(item, dict) and item.get("incident_id") != incident["incident_id"]
            ] if isinstance(existing_recurrences, list) else []
            retained.append({
                "incident_id": incident["incident_id"],
                "recurrence_first_detected_at": incident.get("recurrence_first_detected_at"),
            })
            classification["related_incidents"] = sorted(retained, key=lambda item: str(item["incident_id"]))
            con.execute(
                "UPDATE transaction_records SET classification_json = ? WHERE transaction_id = ?",
                [json.dumps(classification, sort_keys=True), transaction_id],
            )


def _input_matches_scope(transaction_input: dict[str, Any], scope: dict[str, list[str]]) -> bool:
    input_fields = {
        "merchant_id": "merchant_id",
        "issuer_bank": "issuer_bank",
        "issuer_bank_id": "issuer_bank",
        "provider_id": "provider_id",
        "payment_method_category": "payment_method_category",
        "country": "country",
        "currency": "currency",
    }
    for dimension, allowed in scope.items():
        input_field = input_fields.get(dimension)
        if input_field is None or str(transaction_input.get(input_field)) not in allowed:
            return False
    return True


def _refusal_code_summaries(con, incident: dict[str, Any]) -> list[dict[str, Any]]:
    """Create CTR-RFC-002 only from persisted, already-linked transaction facts.

    The join with the canonical event bounds the data to the Incident's window;
    it prevents a later response in the same correlation from being presented as
    evidence for an earlier spike.
    """
    rows = con.execute(
        """SELECT record.input_json, record.classification_json
           FROM transaction_incident_links link
           JOIN transaction_records record ON record.transaction_id = link.transaction_id
           JOIN canonical_events event ON event.event_id = 'evt_' || record.transaction_id
           WHERE link.incident_id = ? AND link.correlation_id = ?
             AND event.event_time >= ? AND event.event_time < ?""",
        [incident["incident_id"], incident["correlation_id"], incident["estimated_started_at"], incident["detected_at"]],
    ).fetchall()
    grouped: dict[tuple[str, str, str, str, str, str, str, str], int] = {}
    for input_json, classification_json in rows:
        if not classification_json:
            continue
        classification = json.loads(classification_json)
        resolution = classification.get("refusal_resolution")
        if not isinstance(resolution, dict) or resolution.get("lookup_status") != "MATCH_FOUND":
            continue
        if resolution.get("outcome") != "FAILED" or not resolution.get("reason"):
            continue
        payload = json.loads(input_json)
        key = (
            str(payload.get("provider_id", "UNKNOWN")), str(payload.get("issuer_bank", "UNKNOWN")),
            str(payload.get("card_brand") or "NOT_APPLICABLE"),
            str(resolution["response_code"]), str(resolution["reason"]),
            str(resolution.get("normalized_code") or "UNMAPPED_DECLINE"),
            str(resolution.get("source") or "UNKNOWN"), str(resolution.get("mapping_version") or "UNKNOWN"),
        )
        grouped[key] = grouped.get(key, 0) + 1
    summaries: list[dict[str, Any]] = []
    for key, count in sorted(grouped.items(), key=lambda item: (-item[1], item[0])):
        provider_id, issuer_bank, card_brand, response_code, reason, normalized_code, source, mapping_version = key
        digest = sha256("|".join(key).encode("utf-8")).hexdigest()[:16]
        summaries.append({"provider_id": provider_id, "issuer_bank": issuer_bank, "card_brand": card_brand,
                          "response_code": response_code, "normalized_code": normalized_code, "reason": reason, "source": source,
                          "mapping_version": mapping_version, "transaction_count": count,
                          "evidence_id": f"evd_refusal_{digest}"})
    return summaries
