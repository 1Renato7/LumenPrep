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


def _set_related_incidents(
    transaction_id: str,
    incident_ids: list[str],
    *,
    evidence_ids: list[str] | None = None,
    correlation_id: str = "corr_inc_001",
) -> None:
    with CONNECTION_LOCK:
        get_connection().execute(
            "UPDATE transaction_records SET classification_json = ?, correlation_id = ? WHERE transaction_id = ?",
            [
                json.dumps(
                    {
                        "category": "PROVIDER_ERROR",
                        "reason": "test",
                        "confidence": 1.0,
                        "evidence_ids": evidence_ids if evidence_ids is not None else ["evt_txn_001"],
                        "related_incident_ids": incident_ids,
                    }
                ),
                correlation_id,
                transaction_id,
            ],
        )


def test_incidents_filter_exposes_only_authorized_transaction_links():
    transaction_id = _submit_transaction()
    _set_related_incidents(transaction_id, ["inc_current_mastercard_001", "inc_not_authorized"])

    response = client.get("/v1/incidents", params={"transaction_id": transaction_id})

    assert response.status_code == 200
    body = response.json()
    assert [item["incident_id"] for item in body] == ["inc_current_mastercard_001"]
    assert all("memory" not in item and "explanation" not in item for item in body)


def test_incidents_filter_returns_empty_list_when_transaction_has_no_incident():
    transaction_id = _submit_transaction()
    _set_related_incidents(transaction_id, [])

    response = client.get("/v1/incidents", params={"transaction_id": transaction_id})

    assert response.status_code == 200
    assert response.json() == []


def test_incidents_filter_rejects_links_without_evidence_or_matching_correlation():
    transaction_id = _submit_transaction()
    _set_related_incidents(
        transaction_id,
        ["inc_current_mastercard_001"],
        evidence_ids=[],
        correlation_id="corr_inc_001",
    )

    without_evidence = client.get("/v1/incidents", params={"transaction_id": transaction_id})
    assert without_evidence.status_code == 200
    assert without_evidence.json() == []

    _set_related_incidents(
        transaction_id,
        ["inc_current_mastercard_001"],
        correlation_id="corr_wrong",
    )
    wrong_correlation = client.get("/v1/incidents", params={"transaction_id": transaction_id})
    assert wrong_correlation.status_code == 200
    assert wrong_correlation.json() == []


def test_transaction_incident_detail_returns_grounded_incident_response():
    transaction_id = _submit_transaction()
    _set_related_incidents(transaction_id, ["inc_current_mastercard_001"])

    response = client.get(f"/v1/transactions/{transaction_id}/incidents")

    assert response.status_code == 200
    body = response.json()
    assert body["schema_version"] == "1.0"
    assert body["transaction_id"] == transaction_id
    assert body["status"] == "RESOLVED"
    assert [item["incident"]["incident_id"] for item in body["incidents"]] == ["inc_current_mastercard_001"]
    assert body["incidents"][0]["evidence_ids"] == ["evt_txn_001"]
    assert {"memory", "explanation"} <= body["incidents"][0].keys()


def test_transaction_incident_detail_reports_no_incident_and_rejections():
    transaction_id = _submit_transaction()
    _set_related_incidents(
        transaction_id,
        ["inc_current_mastercard_001"],
        evidence_ids=[],
    )

    response = client.get(f"/v1/transactions/{transaction_id}/incidents")

    assert response.status_code == 200
    assert response.json()["status"] == "NO_INCIDENT"
    assert response.json()["incidents"] == []
    assert response.json()["rejected_incident_ids"] == ["inc_current_mastercard_001"]


def test_transaction_incident_detail_returns_404_for_unknown_transaction():
    response = client.get("/v1/transactions/txn_unknown/incidents")

    assert response.status_code == 404
    assert response.json()["detail"] == "TRANSACTION_NOT_FOUND"
