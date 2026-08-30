"""CTR-MEM-PROMOTE-001: a graph write requires an explicit human review."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import incidents as incidents_api
from app.incidents import DuckDBIncidentRepository, Incident
from app.memory import InMemoryIncidentRepository
from main import create_app

ROOT = Path(__file__).resolve().parent.parent
REQUEST = json.loads((ROOT / "contracts" / "fixtures" / "incident-confirmation-request.json").read_text(encoding="utf-8"))
RESPONSE_SCHEMA = json.loads((ROOT / "contracts" / "v1" / "incident-confirmation.schema.json").read_text(encoding="utf-8"))

INCIDENT_PAYLOAD = {
    "schema_version": "1.0",
    "incident_id": "inc_confirmation_api_001",
    "state": "SUPPORTED",
    "detected_at": "2026-08-30T12:05:00Z",
    "estimated_started_at": "2026-08-30T12:00:00Z",
    "title": "Payment degradation for country=BR, provider_id=dlocal",
    "scope": {"country": ["BR"], "provider_id": ["dlocal"]},
    "metrics": {"approval_rate_observed": 0.41, "decline_codes": ["PROVIDER_TIMEOUT"]},
    "root_cause": {
        "status": "SUPPORTED",
        "category": "PROVIDER_DEGRADATION",
        "confidence": 0.82,
        "confidence_factors": {"contribution": 0.9},
        "alternatives": [],
    },
    "impact": {"metric": "GMV_AT_RISK", "amount_minor": 4820000, "currency": "BRL", "method": "EXPECTED_APPROVAL_SHORTFALL"},
    "evidence": [{"evidence_id": "evd_confirmation_api", "kind": "DETECTOR_CANDIDATE", "statement": "Detector evidence.", "source_ref": "window://confirmation"}],
    "recommendations": [],
    "limitations": [],
    "correlation_id": "corr_confirmation_api_001",
}


def _persisted_incident() -> Incident:
    return DuckDBIncidentRepository().upsert(Incident.model_validate(INCIDENT_PAYLOAD))


def test_human_confirmation_promotes_only_after_explicit_review_and_is_idempotent():
    incident = _persisted_incident()
    graph = InMemoryIncidentRepository()

    with patch.object(incidents_api, "_memory_repository", return_value=graph), TestClient(create_app()) as client:
        first = client.post(f"/v1/incidents/{incident.incident_id}/confirmation", json=REQUEST)
        replay = client.post(f"/v1/incidents/{incident.incident_id}/confirmation", json=REQUEST)

    assert first.status_code == 200
    assert replay.status_code == 200
    assert first.json() == replay.json()
    assert set(first.json()) == set(RESPONSE_SCHEMA["required"])
    assert first.json()["confirmation"] == "HUMAN_CONFIRMED"
    assert graph.incident_count == 1
    assert DuckDBIncidentRepository().get(incident.incident_id).root_cause.status == "SUPPORTED"


def test_confirmation_rejects_a_second_different_review_without_overwriting_graph_history():
    incident = _persisted_incident()
    graph = InMemoryIncidentRepository()
    conflicting = {**REQUEST, "review_id": "review-demo-002"}

    with patch.object(incidents_api, "_memory_repository", return_value=graph), TestClient(create_app()) as client:
        assert client.post(f"/v1/incidents/{incident.incident_id}/confirmation", json=REQUEST).status_code == 200
        response = client.post(f"/v1/incidents/{incident.incident_id}/confirmation", json=conflicting)

    assert response.status_code == 409
    assert response.json()["detail"] == "INCIDENT_ALREADY_CONFIRMED"
    assert graph.incident_count == 1


def test_confirmation_never_treats_unavailable_graph_memory_as_a_success():
    incident = _persisted_incident()

    with patch.object(incidents_api, "_memory_repository", return_value=None), TestClient(create_app()) as client:
        response = client.post(f"/v1/incidents/{incident.incident_id}/confirmation", json=REQUEST)

    assert response.status_code == 503
    assert response.json()["detail"] == "MEMORY_UNAVAILABLE"


def test_confirmation_rejects_synthetic_or_incomplete_reviews_before_writing():
    incident = _persisted_incident()
    graph = InMemoryIncidentRepository()
    invalid = {**REQUEST, "provenance": "SYNTHETIC_EVALUATION"}

    with patch.object(incidents_api, "_memory_repository", return_value=graph), TestClient(create_app()) as client:
        response = client.post(f"/v1/incidents/{incident.incident_id}/confirmation", json=invalid)

    assert response.status_code == 422
    assert graph.incident_count == 0
