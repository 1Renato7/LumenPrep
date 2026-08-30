"""End-to-end proof that the agent runs off real, persisted engine output.

No Incident is inserted by hand here: canonical events are ingested, the real
pipeline derives the Incident, and the suggestion must be grounded in the
evidence that pipeline actually produced.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.agent import DiagnosticSuggestionRepository
from app.incidents import DuckDBIncidentRepository
from app.ingestion import ingest_event
from app.ingestion.storage import get_connection
from app.worker.incident_pipeline import derive_incidents_for_correlation


def _event(base: dict, *, index: int, when: datetime, correlation_id: str, status: str) -> dict:
    payload = dict(base)
    payload.update(
        {
            "event_id": f"evt_agent_{correlation_id}_{index}",
            "attempt_id": f"att_agent_{correlation_id}_{index}",
            "payment_id": f"pay_agent_{correlation_id}_{index}",
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


def test_pipeline_incident_gets_a_grounded_human_only_suggestion(valid_attempt):
    monday = datetime(2026, 7, 6, 10, tzinfo=timezone.utc)
    for week in range(4):
        _ingest_window(
            valid_attempt,
            start=monday + timedelta(weeks=week),
            correlation_id=f"corr_agent_history_{week}",
            status="SUCCEEDED",
        )
    correlation_id = "corr_agent_anomaly"
    _ingest_window(valid_attempt, start=monday + timedelta(weeks=4), correlation_id=correlation_id, status="DECLINED")

    incident_ids = derive_incidents_for_correlation(get_connection(), correlation_id)
    assert len(incident_ids) == 1

    incident = DuckDBIncidentRepository().get(incident_ids[0])
    suggestion = DiagnosticSuggestionRepository().latest_for_incident(incident_ids[0])
    assert suggestion is not None
    assert suggestion.status in {"SUGGESTED", "INSUFFICIENT_EVIDENCE"}

    # The engine keeps causal authority; the suggestion is a separate record.
    assert incident.root_cause.status == "SUPPORTED"
    assert suggestion.status != incident.root_cause.status

    allowed = {item.evidence_id for item in incident.evidence}
    cited = {
        evidence_id
        for reason in suggestion.reasons
        for evidence_id in reason.evidence_ids
    } | {
        evidence_id
        for action in suggestion.recommended_actions
        for evidence_id in action.rationale_evidence_ids
    }
    assert cited <= allowed, "the agent may only cite evidence the pipeline persisted"
    assert all(action.execution == "HUMAN_ONLY" for action in suggestion.recommended_actions)


def test_reprocessing_the_same_correlation_keeps_one_suggestion(valid_attempt):
    monday = datetime(2026, 7, 6, 10, tzinfo=timezone.utc)
    for week in range(4):
        _ingest_window(
            valid_attempt,
            start=monday + timedelta(weeks=week),
            correlation_id=f"corr_agent_idem_history_{week}",
            status="SUCCEEDED",
        )
    correlation_id = "corr_agent_idem"
    _ingest_window(valid_attempt, start=monday + timedelta(weeks=4), correlation_id=correlation_id, status="DECLINED")

    first = derive_incidents_for_correlation(get_connection(), correlation_id)
    second = derive_incidents_for_correlation(get_connection(), correlation_id)

    assert second == first
    assert DiagnosticSuggestionRepository().count_for_incident(first[0]) == 1
