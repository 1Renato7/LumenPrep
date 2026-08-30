"""Derive and persist current Incidents after a terminal canonical event.

The pipeline consumes only persisted aggregate windows and detector candidates.
It deliberately does not consult memory, prompt an LLM, or turn an RCA hypothesis
into a supported cause.  Memory/explanation remain read-time enrichment of the
already-persisted current Incident.
"""

from __future__ import annotations

import json
import logging
from hashlib import sha256
from typing import Any

from app.agent import DiagnosticAgentService
from app.aggregation import WindowMetrics, compute_windows
from app.detection import detect_candidates
from app.incidents import DuckDBIncidentRepository, Evidence, Incident, correlate_candidates, compute_impact, to_incident
from app.rca import explore_slices, rank_hypotheses

logger = logging.getLogger(__name__)

LOW_SAMPLE_ATTEMPTS = 12


def derive_incidents_for_correlation(con, correlation_id: str) -> list[str]:
    """Persist newly observed Incident groups and return their stable IDs.

    Detector history may contain other correlations, but only candidates produced
    for the just-processed correlation may create or update its Incidents.
    """
    windows = compute_windows(con)
    candidates = [
        candidate
        for candidate in detect_candidates(windows, low_sample_attempts=LOW_SAMPLE_ATTEMPTS)
        if candidate.correlation_id == correlation_id and candidate.slice
    ]
    if not candidates:
        return []

    repository = DuckDBIncidentRepository()
    incident_ids: list[str] = []
    for group in correlate_candidates(_most_specific_candidates(candidates)):
        window = _window_for_group(windows, group.correlation_id, group.candidates[0])
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
        persisted = repository.upsert(incident)
        _link_matching_transactions(con, repository, persisted.model_dump(mode="json"))
        _suggest_for_persisted_incident(persisted, window.decline_profile)
        incident_ids.append(persisted.incident_id)
    return incident_ids


def _suggest_for_persisted_incident(incident: Incident, decline_profile: dict[str, int]) -> None:
    """Run the proactive agent on an Incident that is already durable.

    This call is deliberately last and deliberately swallowed.  It runs inside
    the worker's DuckDB transaction, so an agent error escaping here would roll
    back the transaction lifecycle it has nothing to do with.  Detection, the
    Incident and the deterministic explanation must survive a model that is
    slow, unavailable or wrong.
    """
    try:
        DiagnosticAgentService().suggest_for_incident(incident, decline_profile=decline_profile)
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
    if not profile:
        return fallback or "UNCLASSIFIED_DEGRADATION"
    code = max(profile.items(), key=lambda item: item[1])[0]
    if code.startswith("PROVIDER_"):
        return "PROVIDER_DEGRADATION"
    if code.startswith("ISSUER_") or code in {"DO_NOT_HONOR", "INSUFFICIENT_FUNDS", "TRANSACTION_NOT_PERMITTED"}:
        return "ISSUER_OUTAGE"
    if code in {"METHOD_UNAVAILABLE", "CASH_IN_STORE_UNAVAILABLE"}:
        return "PAYMENT_METHOD_DEGRADATION"
    return fallback or "UNCLASSIFIED_DEGRADATION"


def _link_matching_transactions(con, repository: DuckDBIncidentRepository, incident: dict[str, Any]) -> None:
    """Link only records with matching correlation, scope and existing evidence."""
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
        if incident["incident_id"] not in related:
            related.append(incident["incident_id"])
            classification["related_incident_ids"] = sorted(related)
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
