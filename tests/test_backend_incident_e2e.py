"""The public batch path must create a current Incident without DB fixtures."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from itertools import count

from fastapi.testclient import TestClient

from app.api import incidents as incidents_api
from app.simulation.transaction_outcomes import AdaptedTransaction
from app.worker import transaction_worker as worker
from main import app


_KEYS = count()


def _transaction(occurred_at: datetime, *, decline: bool) -> dict[str, object]:
    return {
        "client_reference": "decline" if decline else "success",
        "occurred_at": occurred_at.isoformat().replace("+00:00", "Z"),
        "merchant_id": "merchant_br_01",
        "provider_id": "provider_alpha",
        "issuer_bank": "bank_br_a",
        "country": "BR",
        "currency": "BRL",
        "amount_minor": 12_990,
        "payment_method_category": "CARD",
        "card_brand": "VISA",
        "card_type": "CREDIT",
        "channel": "WEB",
    }


def _adapt(transaction_id: str, transaction: dict, correlation_id: str) -> AdaptedTransaction:
    declined = transaction.get("client_reference") == "decline"
    status = "DECLINED" if declined else "SUCCEEDED"
    result = "FAILED" if declined else "SUCCEEDED"
    when = str(transaction["occurred_at"])
    event = {
        "schema_version": "1.0",
        "event_id": f"evt_{transaction_id}",
        "event_type": "PAYMENT_ATTEMPT_CREATED",
        "event_time": when,
        "received_at": when,
        "payment_id": f"pay_{transaction_id}",
        "attempt_id": f"att_{transaction_id}",
        "attempt_sequence": 1,
        "merchant_id": transaction["merchant_id"],
        "provider_id": transaction["provider_id"],
        "provider_connection_id": None,
        "country": transaction["country"],
        "currency": transaction["currency"],
        "amount_minor": transaction["amount_minor"],
        "payment_method_category": "CARD",
        "payment_method_type": "CREDIT",
        "card": {"brand": "VISA", "type": "CREDIT", "issuer_bank_id": transaction["issuer_bank"], "issuer_country": "BR", "bin_prefix": None},
        "status": status,
        "decline": (
            {"normalized_code": "PROVIDER_TIMEOUT", "category": "PROVIDER", "retryability": "RETRY_LATER", "raw_code": "68", "raw_message": "Timed out", "mapping_version": "1.0"}
            if declined
            else None
        ),
        "timing": {"orchestrator_latency_ms": 20, "provider_latency_ms": 2_000 if declined else 100, "total_latency_ms": 2_020 if declined else 120},
        "raw_event_id": None,
        "normalization_version": "1.0",
        "correlation_id": correlation_id,
        "is_test": True,
    }
    return AdaptedTransaction(
        result=result,
        outcome={"result": result, "provider_response_code": "68" if declined else "00", "normalized_decline_code": "PROVIDER_TIMEOUT" if declined else None, "latency_ms": event["timing"]["total_latency_ms"]},
        classification={"category": "PROVIDER_ERROR" if declined else "APPROVED", "reason": "Deterministic E2E outcome.", "confidence": 0.9, "evidence_ids": [f"evd_{transaction_id}"], "related_incident_ids": []},
        event=event,
    )


def _submit(client: TestClient, start: datetime, *, decline: bool) -> list[str]:
    key = f"incident-e2e-{next(_KEYS):04d}"
    response = client.post(
        "/v1/transaction-batches",
        json={
            "schema_version": "1.0",
            "idempotency_key": key,
            "transactions": [_transaction(start + timedelta(seconds=index), decline=decline) for index in range(12)],
        },
        headers={"Idempotency-Key": key},
    )
    assert response.status_code == 202
    return response.json()["transaction_ids"]


def test_batch_to_incident_to_grounded_detail_uses_no_fixture(monkeypatch):
    monkeypatch.setattr(incidents_api.settings, "demo_mode", False)
    monkeypatch.setattr(worker, "_generate_outcome", _adapt)
    client = TestClient(app)
    monday = datetime(2026, 7, 6, 10, tzinfo=timezone.utc)

    for week in range(4):
        _submit(client, monday + timedelta(weeks=week), decline=False)
    anomaly_transaction_ids = _submit(client, monday + timedelta(weeks=4), decline=True)

    detail = client.get(f"/v1/transactions/{anomaly_transaction_ids[0]}/incidents")

    assert detail.status_code == 200
    body = detail.json()
    assert body["status"] == "RESOLVED"
    assert len(body["incidents"]) == 1
    incident = body["incidents"][0]["incident"]
    assert incident["state"] == incident["root_cause"]["status"] == "SUPPORTED"
    assert incident["root_cause"]["category"] == "PROVIDER_DEGRADATION"
    assert body["incidents"][0]["evidence_ids"] == [f"evd_{anomaly_transaction_ids[0]}"]
    assert "fixture://" not in str(body)

    trigger_detail = client.get(f"/v1/transactions/{anomaly_transaction_ids[-1]}/incidents")
    assert trigger_detail.status_code == 200
    assert trigger_detail.json()["status"] == "RESOLVED"
    assert trigger_detail.json()["incidents"][0]["evidence_ids"] == [f"evd_{anomaly_transaction_ids[-1]}"]
