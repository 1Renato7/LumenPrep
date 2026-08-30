"""The suggestion endpoint and the pipeline hook.

Two invariants matter here: the additive endpoint never changes the frozen
``CTR-INC-001`` payload, and a failing agent never costs us the Incident.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.agent import DiagnosticAgentService, DiagnosticSuggestionRepository
from app.incidents import DuckDBIncidentRepository, Incident
from app.worker import incident_pipeline
from main import create_app

ROOT = Path(__file__).resolve().parent.parent
SUGGESTION_SCHEMA = json.loads(
    (ROOT / "contracts" / "v1" / "agent-diagnostic-suggestion.schema.json").read_text(encoding="utf-8")
)

INCIDENT_PAYLOAD = {
    "schema_version": "1.0",
    "incident_id": "inc_api_agent_001",
    "state": "SUPPORTED",
    "detected_at": "2026-08-30T12:05:00Z",
    "estimated_started_at": "2026-08-30T12:00:00Z",
    "title": "Payment degradation for country=BR, provider_id=dlocal",
    "scope": {"country": ["BR"], "provider_id": ["dlocal"]},
    "metrics": {
        "eligible_attempts": 240,
        "approval_rate_observed": 0.41,
        "approval_rate_expected": 0.87,
        "lost_approvals": 110,
    },
    "root_cause": {
        "status": "SUPPORTED",
        "category": "PROVIDER_DEGRADATION",
        "confidence": 0.82,
        "confidence_factors": {"contribution": 0.9},
        "alternatives": [],
    },
    "impact": {
        "metric": "GMV_AT_RISK",
        "amount_minor": 4820000,
        "currency": "BRL",
        "method": "EXPECTED_APPROVAL_SHORTFALL",
    },
    "evidence": [
        {
            "evidence_id": "evd_det_api",
            "kind": "DETECTOR_CANDIDATE",
            "statement": "Detector candidate cand_api contributed to this Incident.",
            "source_ref": "window://2026-08-30T12:00:00Z/provider_id=dlocal",
        },
        {
            "evidence_id": "evd_decline_api",
            "kind": "DECLINE_PROFILE",
            "statement": "Dominant decline profile is PROVIDER_TIMEOUT across 96 eligible attempts in this slice.",
            "source_ref": "window://decline-profile",
        },
    ],
    "recommendations": [],
    "limitations": [],
    "correlation_id": "corr_api_agent_001",
}


def _persisted_incident() -> Incident:
    return DuckDBIncidentRepository().upsert(Incident.model_validate(INCIDENT_PAYLOAD))


def test_suggestion_endpoint_returns_the_persisted_hypothesis():
    incident = _persisted_incident()
    DiagnosticAgentService().suggest_for_incident(incident, decline_profile={"PROVIDER_TIMEOUT": 96})

    with TestClient(create_app()) as client:
        response = client.get(f"/v1/incidents/{incident.incident_id}/suggestion")

    assert response.status_code == 200
    body = response.json()
    assert body["incident_id"] == incident.incident_id
    assert body["status"] == "SUGGESTED"
    assert set(body) == set(SUGGESTION_SCHEMA["required"])
    assert all(action["execution"] == "HUMAN_ONLY" for action in body["recommended_actions"])


def test_suggestion_endpoint_is_explicit_when_nothing_was_generated():
    incident = _persisted_incident()

    with TestClient(create_app()) as client:
        response = client.get(f"/v1/incidents/{incident.incident_id}/suggestion")

    assert response.status_code == 404
    assert response.json()["detail"] == "SUGGESTION_NOT_AVAILABLE"


def test_suggestion_endpoint_404s_for_an_unknown_incident():
    with TestClient(create_app()) as client:
        response = client.get("/v1/incidents/inc_does_not_exist/suggestion")

    assert response.status_code == 404
    assert response.json()["detail"] == "INCIDENT_NOT_FOUND"


def test_incident_payload_is_unchanged_by_the_agent():
    """CTR-INC-001 v1 stays frozen: no suggestion field leaks into the Incident."""
    incident = _persisted_incident()
    DiagnosticAgentService().suggest_for_incident(incident, decline_profile={"PROVIDER_TIMEOUT": 96})

    with TestClient(create_app()) as client:
        response = client.get(f"/v1/incidents/{incident.incident_id}")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"incident", "memory", "explanation"}
    assert "suggestion" not in body["incident"]
    assert body["incident"]["root_cause"]["status"] == "SUPPORTED"
    assert body["incident"]["root_cause"]["category"] == "PROVIDER_DEGRADATION"


def test_agent_failure_does_not_break_incident_persistence(monkeypatch):
    """The hook runs inside the worker's DuckDB transaction; it must never raise."""

    class Exploding:
        def suggest_for_incident(self, *args, **kwargs):
            raise RuntimeError("agent exploded")

    monkeypatch.setattr(incident_pipeline, "DiagnosticAgentService", lambda: Exploding())
    incident = _persisted_incident()

    incident_pipeline._suggest_for_persisted_incident(incident, {"PROVIDER_TIMEOUT": 96})

    assert DuckDBIncidentRepository().get(incident.incident_id) is not None
    assert DiagnosticSuggestionRepository().latest_for_incident(incident.incident_id) is None
