"""TASK-INT-001/002 fixture-backed preflight smoke."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.aggregation import get_current_metrics
from app.api.incidents import build_incident_response
from app.ingestion import ingest_event
from app.incidents import RootCause, compute_impact, correlate_candidates, to_incident

_FIXTURES = Path(__file__).resolve().parents[2] / "contracts" / "fixtures"


def _fixture(name: str) -> dict[str, Any]:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


def _with_key(payload: dict[str, Any], key: str, value: str) -> dict[str, Any]:
    result = dict(payload)
    result[key] = value
    return result


def run_smoke() -> dict[str, Any]:
    """Exercise public seams in order without directly touching storage.

    TODO(TASK-RCA-002, TASK-EXP-003, TASK-DATA-006): replace fixture inputs and
    response components when their real producers are available.
    """
    ingest = ingest_event(_fixture("canonical-attempt.json"))
    metrics = get_current_metrics()
    groups = correlate_candidates([_fixture("anomaly-candidate.json")])
    if len(groups) != 1:
        raise AssertionError("fixture candidate must create one incident group")

    incident = to_incident(
        groups[0],
        compute_impact(groups[0], metrics[0]),
        RootCause(status="INCONCLUSIVE", category=None, confidence=0.0, confidence_factors={"fixture": 0.0}),
        incident_id="smoke_fixture_incident",
        title="Fixture smoke incident",
        evidence=[
            {
                "evidence_id": "smoke_candidate",
                "kind": "METRIC_SHIFT",
                "statement": "Fixture anomaly candidate reached the incident seam.",
                "source_ref": "fixture://anomaly-candidate.json",
            }
        ],
        recommendations=[],
        limitations=["Fixture-only smoke pending real upstream producers."],
    )
    response = build_incident_response(
        incident.model_dump(),
        _with_key(_fixture("similar-incidents-empty.json"), "query_incident_id", incident.incident_id),
        _with_key(_fixture("explanation-bundle-no-precedent.json"), "incident_id", incident.incident_id),
    )
    return {
        "ingestion_status": ingest.status,
        "metrics_count": len(metrics),
        "incident_id": response["incident"]["incident_id"],
        "memory_status": response["memory"]["memory_status"],
    }
