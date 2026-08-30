from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.incidents import DuckDBIncidentRepository
from app.ingestion import ingest_event
from app.ingestion.storage import get_connection
from app.worker.incident_pipeline import derive_incidents_for_correlation


def _event(base: dict, *, index: int, when: datetime, correlation_id: str, status: str) -> dict:
    payload = dict(base)
    payload.update(
        {
            "event_id": f"evt_pipeline_{correlation_id}_{index}",
            "attempt_id": f"att_pipeline_{correlation_id}_{index}",
            "payment_id": f"pay_pipeline_{correlation_id}_{index}",
            "event_time": when.isoformat().replace("+00:00", "Z"),
            "received_at": when.isoformat().replace("+00:00", "Z"),
            "correlation_id": correlation_id,
            "provider_id": "stripe",
            "country": "BR",
            "currency": "BRL",
            "amount_minor": 1000,
            "status": status,
            "decline": None if status == "SUCCEEDED" else base["decline"],
            "timing": {
                "orchestrator_latency_ms": 20,
                "provider_latency_ms": 100 if status == "SUCCEEDED" else 2_000,
                "total_latency_ms": 120 if status == "SUCCEEDED" else 2_020,
            },
        }
    )
    return payload


def _ingest_window(base: dict, *, start: datetime, correlation_id: str, status: str, count: int = 12) -> None:
    for index in range(count):
        result = ingest_event(
            _event(base, index=index, when=start + timedelta(seconds=index), correlation_id=correlation_id, status=status)
        )
        assert result.status == "ACCEPTED"


def test_pipeline_persists_one_inconclusive_incident_and_is_idempotent(valid_attempt):
    monday = datetime(2026, 7, 6, 10, tzinfo=timezone.utc)
    for week in range(4):
        _ingest_window(valid_attempt, start=monday + timedelta(weeks=week), correlation_id=f"corr_history_{week}", status="SUCCEEDED")

    anomaly_correlation = "corr_current_anomaly"
    _ingest_window(valid_attempt, start=monday + timedelta(weeks=4), correlation_id=anomaly_correlation, status="DECLINED")

    first = derive_incidents_for_correlation(get_connection(), anomaly_correlation)
    second = derive_incidents_for_correlation(get_connection(), anomaly_correlation)

    assert len(first) == 1
    assert second == first
    persisted = DuckDBIncidentRepository().get(first[0])
    assert persisted is not None
    assert persisted.state == "INCONCLUSIVE"
    assert persisted.root_cause.status == "INCONCLUSIVE"
    assert persisted.root_cause.alternatives
    assert persisted.correlation_id == anomaly_correlation


def test_pipeline_does_not_create_incident_for_low_sample_anomaly(valid_attempt):
    monday = datetime(2026, 7, 6, 10, tzinfo=timezone.utc)
    _ingest_window(valid_attempt, start=monday, correlation_id="corr_history", status="SUCCEEDED")
    _ingest_window(
        valid_attempt,
        start=monday + timedelta(weeks=4),
        correlation_id="corr_low_sample",
        status="DECLINED",
        count=11,
    )

    assert derive_incidents_for_correlation(get_connection(), "corr_low_sample") == []
    assert DuckDBIncidentRepository().list() == []
