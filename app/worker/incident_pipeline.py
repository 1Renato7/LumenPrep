"""Derive and persist current Incidents after a terminal canonical event.

The pipeline consumes only persisted aggregate windows and detector candidates.
It deliberately does not consult memory, prompt an LLM, or turn an RCA hypothesis
into a supported cause.  Memory/explanation remain read-time enrichment of the
already-persisted current Incident.
"""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

from app.aggregation import WindowMetrics, compute_windows
from app.detection import detect_candidates
from app.incidents import DuckDBIncidentRepository, Evidence, correlate_candidates, compute_impact, to_incident
from app.rca import explore_slices, rank_hypotheses

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
        if candidate.correlation_id == correlation_id
    ]
    if not candidates:
        return []

    repository = DuckDBIncidentRepository()
    incident_ids: list[str] = []
    for group in correlate_candidates(candidates):
        window = _window_for_group(windows, group.correlation_id, group.candidates[0])
        if window is None:
            continue
        ranking = rank_hypotheses(explore_slices(group.candidates, min_support=LOW_SAMPLE_ATTEMPTS))
        incident = to_incident(
            group,
            compute_impact(group, window),
            ranking.to_root_cause(),
            incident_id=_incident_id(group.correlation_id, window, group.scope),
            title=_title(group.scope),
            evidence=_evidence(group.candidates),
            recommendations=[],
            limitations=(
                "RCA hypotheses are ranked for investigation; current causal status remains INCONCLUSIVE.",
            ),
        )
        persisted = repository.upsert(incident)
        _link_matching_transactions(con, repository, persisted.model_dump(mode="json"))
        incident_ids.append(persisted.incident_id)
    return incident_ids


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
    return f"Inconclusive payment degradation for {label}"


def _evidence(candidates: tuple[dict[str, Any], ...]) -> list[Evidence]:
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
    return list({item.evidence_id: item for item in values}.values())


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
        "issuer_bank": "issuer_bank",
        "provider_id": "provider_id",
        "country": "country",
        "currency": "currency",
    }
    for dimension, allowed in scope.items():
        input_field = input_fields.get(dimension)
        if input_field is None or str(transaction_input.get(input_field)) not in allowed:
            return False
    return True
