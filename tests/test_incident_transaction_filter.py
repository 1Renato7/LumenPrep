import json

from fastapi.testclient import TestClient

from app.ingestion.storage import CONNECTION_LOCK, get_connection
from main import app


client = TestClient(app)


def _submit_transaction() -> str:
    payload = {
        "schema_version": "1.0",
        "idempotency_key": "incident-filter-key-0001",
        "transactions": [
            {
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
        ],
    }
    response = client.post("/v1/transaction-batches", json=payload, headers={"Idempotency-Key": payload["idempotency_key"]})
    assert response.status_code == 202
    return response.json()["transaction_ids"][0]


def _set_related_incidents(transaction_id: str, incident_ids: list[str]) -> None:
    with CONNECTION_LOCK:
        get_connection().execute(
            "UPDATE transaction_records SET classification_json = ? WHERE transaction_id = ?",
            [
                json.dumps(
                    {
                        "category": "PROVIDER_ERROR",
                        "reason": "test",
                        "confidence": 1.0,
                        "evidence_ids": [],
                        "related_incident_ids": incident_ids,
                    }
                ),
                transaction_id,
            ],
        )


def test_incidents_filter_exposes_only_authorized_transaction_links():
    transaction_id = _submit_transaction()
    _set_related_incidents(transaction_id, ["inc_current_mastercard_001", "inc_not_authorized"])

    response = client.get("/v1/incidents", params={"transaction_id": transaction_id})

    assert response.status_code == 200
    body = response.json()
    assert [item["incident"]["incident_id"] for item in body] == ["inc_current_mastercard_001"]
    assert all({"incident", "memory", "explanation"} <= item.keys() for item in body)


def test_incidents_filter_returns_empty_list_when_transaction_has_no_incident():
    transaction_id = _submit_transaction()
    _set_related_incidents(transaction_id, [])

    response = client.get("/v1/incidents", params={"transaction_id": transaction_id})

    assert response.status_code == 200
    assert response.json() == []
