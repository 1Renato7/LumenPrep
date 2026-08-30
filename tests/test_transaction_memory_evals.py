"""TASK-MEM-009: transaction-to-memory evaluation cases for the public detail route."""

from __future__ import annotations

import json
from itertools import count

import pytest
from fastapi.testclient import TestClient

from app.api import incidents as incidents_api
from app.ingestion.storage import CONNECTION_LOCK, get_connection
from app.memory import MemoryStatus
from app.memory.models import RetrievalTrace, SimilarIncidentResult
from app.simulation.background_traffic import submit_background_batch
from main import app


client = TestClient(app)
_REQUEST_SEQUENCE = count()


@pytest.fixture(autouse=True)
def _explicit_demo_incident_adapter(monkeypatch):
    monkeypatch.setattr(incidents_api.settings, "demo_mode", True)


def _transaction() -> dict[str, object]:
    return {
        "merchant_id": "merchant_br_01",
        "provider_id": "provider_alpha",
        "issuer_bank": "bank_br_a",
        "country": "BR",
        "currency": "BRL",
        "amount_minor": 12990,
        "payment_method_category": "CARD",
        "card_brand": "VISA",
        "card_type": "CREDIT",
        "channel": "WEB",
    }


def _submit_transactions(transactions: list[dict[str, object]]) -> list[str]:
    request_number = next(_REQUEST_SEQUENCE)
    payload = {
        "schema_version": "1.0",
        "idempotency_key": f"mem-eval-{request_number:04d}",
        "transactions": transactions,
    }
    response = client.post("/v1/transaction-batches", json=payload, headers={"Idempotency-Key": payload["idempotency_key"]})
    assert response.status_code == 202
    return response.json()["transaction_ids"]


def _author_transaction(
    transaction_id: str,
    *,
    incident_ids: list[str],
    evidence_ids: list[str],
    correlation_id: str = "corr_inc_001",
    failed: bool = False,
) -> None:
    outcome = {"status": "FAILED", "reason": "evaluation-only"} if failed else None
    classification = {
        "category": "PROVIDER_ERROR",
        "reason": "evaluation-only",
        "confidence": 1.0,
        "evidence_ids": evidence_ids,
        "related_incident_ids": incident_ids,
    }
    with CONNECTION_LOCK:
        get_connection().execute(
            """UPDATE transaction_records
               SET status = CASE WHEN ? THEN 'FAILED' ELSE status END,
                   outcome_json = ?, classification_json = ?, correlation_id = ?
               WHERE transaction_id = ?""",
            [failed, json.dumps(outcome) if outcome else None, json.dumps(classification), correlation_id, transaction_id],
        )


def _keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_keys(item) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(_keys(item) for item in value)) if value else set()
    return set()


def test_failed_transaction_without_incident_does_not_invent_memory_or_explanation():
    transaction_id = _submit_transactions([_transaction()])[0]
    _author_transaction(
        transaction_id,
        incident_ids=[],
        evidence_ids=["evt-failed-without-incident"],
        failed=True,
    )

    response = client.get(f"/v1/transactions/{transaction_id}/incidents")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NO_INCIDENT"
    assert body["incidents"] == []
    assert {"memory", "explanation", "seed", "ground_truth", "generator_config"}.isdisjoint(_keys(body))


def test_shared_incident_keeps_each_transaction_evidence_in_its_own_scope():
    first_transaction_id, second_transaction_id = _submit_transactions([_transaction(), _transaction()])
    _author_transaction(
        first_transaction_id,
        incident_ids=["inc_current_mastercard_001"],
        evidence_ids=["evt-first-transaction"],
    )
    _author_transaction(
        second_transaction_id,
        incident_ids=["inc_current_mastercard_001"],
        evidence_ids=["evt-second-transaction"],
    )

    first = client.get(f"/v1/transactions/{first_transaction_id}/incidents")
    second = client.get(f"/v1/transactions/{second_transaction_id}/incidents")

    assert first.status_code == second.status_code == 200
    first_link = first.json()["incidents"][0]
    second_link = second.json()["incidents"][0]
    assert first_link["incident"]["incident_id"] == second_link["incident"]["incident_id"]
    assert first_link["evidence_ids"] == ["evt-first-transaction"]
    assert second_link["evidence_ids"] == ["evt-second-transaction"]
    assert "evt-second-transaction" not in json.dumps(first.json())
    assert "evt-first-transaction" not in json.dumps(second.json())


def test_sample_seed_and_internal_configuration_do_not_reach_grounded_detail():
    sampled = client.post(
        "/v1/transaction-samples",
        json={"schema_version": "1.0", "count": 1, "seed": 424242},
    )
    assert sampled.status_code == 200
    transaction_id = _submit_transactions(sampled.json()["transactions"])[0]
    _author_transaction(
        transaction_id,
        incident_ids=["inc_current_mastercard_001"],
        evidence_ids=["evt-sampled-transaction"],
    )

    response = client.get(f"/v1/transactions/{transaction_id}/incidents")

    assert response.status_code == 200
    serialized = json.dumps(response.json())
    assert "424242" not in serialized
    assert "sample-" not in serialized
    assert "ground_truth" not in serialized
    assert "generator_config" not in serialized
    assert response.json()["incidents"][0]["explanation"]["model_version"] == "deterministic-template"


def test_memory_unavailable_keeps_current_cause_and_deterministic_explanation(monkeypatch):
    def unavailable_memory(_, incident):
        return SimilarIncidentResult(
            query_incident_id=incident.incident_id,
            memory_status=MemoryStatus.MEMORY_UNAVAILABLE,
            matches=(),
            retrieval_trace=RetrievalTrace(
                cypher_filter="evaluation memory unavailable",
                candidate_count=0,
                embedding_model=None,
                index_version="incident-memory-v1",
                fallback_used=True,
            ),
            correlation_id=incident.correlation_id,
        )

    monkeypatch.setattr(incidents_api.IncidentMemoryService, "retrieve", unavailable_memory)
    transaction_id = _submit_transactions([_transaction()])[0]
    _author_transaction(
        transaction_id,
        incident_ids=["inc_current_mastercard_001"],
        evidence_ids=["evt-memory-unavailable"],
    )

    response = client.get(f"/v1/transactions/{transaction_id}/incidents")

    assert response.status_code == 200
    link = response.json()["incidents"][0]
    assert link["memory"]["memory_status"] == "MEMORY_UNAVAILABLE"
    assert link["incident"]["root_cause"]["status"] == "SUPPORTED"
    assert link["explanation"]["model_version"] == "deterministic-template"
    assert any("memory is unavailable" in item.lower() for item in link["explanation"]["limitations"])


def test_processed_background_traffic_has_no_incident_detail_until_rca_authors_a_link():
    batch = submit_background_batch(2, seed=707)

    details = [client.get(f"/v1/transactions/{transaction_id}/incidents") for transaction_id in batch["transaction_ids"]]

    assert all(response.status_code == 200 for response in details)
    assert all(response.json()["status"] == "NO_INCIDENT" for response in details)
    assert all(response.json()["incidents"] == [] for response in details)
    assert all("707" not in json.dumps(response.json()) for response in details)
