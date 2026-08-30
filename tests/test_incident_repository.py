from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api import incidents as incidents_api
from app.incidents import DuckDBIncidentRepository, Incident, IncidentIdConflictError
from app.ingestion.storage import get_connection
from main import app


def _incident(incident_id: str, *, scope: dict[str, list[str]] | None = None, correlation_id: str = "corr_repo", detected_at: str = "2026-08-30T12:05:00Z") -> Incident:
    return Incident.model_validate(
        {
            "schema_version": "1.0",
            "incident_id": incident_id,
            "state": "SUPPORTED",
            "detected_at": detected_at,
            "estimated_started_at": detected_at.replace("12:05", "12:00"),
            "title": "Provider degradation",
            "scope": scope or {"provider_id": ["provider_alpha"], "country": ["BR"]},
            "metrics": {"eligible_attempts": 100},
            "root_cause": {
                "status": "SUPPORTED",
                "category": "PROVIDER_DEGRADATION",
                "confidence": 0.9,
                "confidence_factors": {"test": 0.9},
            },
            "impact": {"metric": "GMV_AT_RISK", "amount_minor": 1000, "currency": "BRL", "method": "EXPECTED_APPROVAL_SHORTFALL"},
            "evidence": [{"evidence_id": "evd_repo", "kind": "METRIC_SHIFT", "statement": "Test evidence.", "source_ref": "test://repository"}],
            "recommendations": [],
            "limitations": [],
            "correlation_id": correlation_id,
        }
    )


def test_upsert_is_idempotent_by_window_and_full_causal_scope():
    repository = DuckDBIncidentRepository()
    first = repository.upsert(_incident("inc_first"))
    redelivery = repository.upsert(_incident("inc_redelivery"))

    assert redelivery.incident_id == first.incident_id
    assert [item.incident_id for item in repository.list()] == [first.incident_id]


def test_notification_is_persistent_and_idempotent_for_one_new_incident():
    repository = DuckDBIncidentRepository()
    incident, created = repository.upsert_with_status(_incident("inc_notification"))
    assert created is True
    repository.create_notification(incident.incident_id)
    repository.create_notification(incident.incident_id)
    notifications = repository.notifications()
    assert len(notifications) == 1
    assert notifications[0]["read_at"] is None
    assert repository.mark_notification_read(notifications[0]["notification_id"]) is True
    assert repository.mark_notification_read(notifications[0]["notification_id"]) is True
    assert repository.notifications()[0]["read_at"] is not None


def test_simultaneous_distinct_causal_fingerprints_remain_separate():
    repository = DuckDBIncidentRepository()
    provider = repository.upsert(_incident("inc_provider"))
    issuer = repository.upsert(_incident("inc_issuer", scope={"issuer_bank": ["bank_br_a"], "country": ["BR"]}))

    assert {item.incident_id for item in repository.list()} == {provider.incident_id, issuer.incident_id}


def test_incident_id_cannot_be_reused_for_a_different_fingerprint():
    repository = DuckDBIncidentRepository()
    repository.upsert(_incident("inc_shared"))

    with pytest.raises(IncidentIdConflictError):
        repository.upsert(_incident("inc_shared", scope={"issuer_bank": ["bank_br_a"], "country": ["BR"]}))


def test_recurrence_preserves_first_detection_across_windows_and_correlations():
    repository = DuckDBIncidentRepository()
    first = repository.upsert(_incident("inc_week_one", correlation_id="corr_week_one", detected_at="2026-08-23T12:05:00Z"))
    recurrence = repository.upsert(_incident("inc_week_two", correlation_id="corr_week_two", detected_at="2026-08-30T12:05:00Z"))
    different_scope = repository.upsert(_incident("inc_other_scope", correlation_id="corr_week_two", scope={"provider_id": ["provider_beta"], "country": ["BR"]}, detected_at="2026-08-30T12:05:00Z"))

    assert first.recurrence_first_detected_at == "2026-08-23T12:05:00Z"
    assert recurrence.recurrence_first_detected_at == first.recurrence_first_detected_at
    assert different_scope.recurrence_first_detected_at == "2026-08-30T12:05:00Z"


def test_transaction_link_requires_matching_correlation_and_evidence():
    repository = DuckDBIncidentRepository()
    incident = repository.upsert(_incident("inc_link"))
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    get_connection().execute(
        """INSERT INTO transaction_records
           (transaction_id, batch_id, batch_position, created_at, updated_at, status, input_json, processing_json, correlation_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ["txn_link", "batch_link", 0, now, now, "SUCCEEDED", "{}", "{}", "corr_repo"],
    )

    repository.link_transaction("txn_link", incident.incident_id, evidence_ids=["evd_repo"], correlation_id="corr_repo")

    assert [item.incident_id for item in repository.list_for_transaction("txn_link")] == [incident.incident_id]
    with pytest.raises(ValueError, match="correlations"):
        repository.link_transaction("txn_link", incident.incident_id, evidence_ids=["evd_repo"], correlation_id="corr_other")


def test_live_incident_endpoint_reads_only_the_persisted_repository(monkeypatch):
    monkeypatch.setattr(incidents_api.settings, "demo_mode", False)
    stored = DuckDBIncidentRepository().upsert(_incident("inc_live"))

    response = TestClient(app).get("/v1/incidents")

    assert response.status_code == 200
    assert [item["incident_id"] for item in response.json()] == [stored.incident_id]
    assert TestClient(app).get("/v1/incidents/inc_current_mastercard_001").status_code == 404
