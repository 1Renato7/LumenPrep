from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

from fastapi.testclient import TestClient

from app.config import settings
from main import app

client = TestClient(app)


def _transaction(*, amount_minor: int = 12990) -> dict:
    return {
        "merchant_id": "merchant_br_01",
        "provider_id": "provider_alpha",
        "issuer_bank": "bank_br_a",
        "country": "BR",
        "currency": "BRL",
        "amount_minor": amount_minor,
        "payment_method_category": "CARD",
        "card_brand": "VISA",
        "card_type": "CREDIT",
        "channel": "WEB",
    }


def _batch(key: str = "batch-key-0001", *, amount_minor: int = 12990) -> dict:
    return {"schema_version": "1.0", "idempotency_key": key, "transactions": [_transaction(amount_minor=amount_minor)]}


def _submit(payload: dict):
    return client.post("/v1/transaction-batches", json=payload, headers={"Idempotency-Key": payload["idempotency_key"]})


def test_catalog_and_seeded_samples_are_public_facts_only():
    catalog = client.get("/v1/transaction-catalog")
    assert catalog.status_code == 200
    assert catalog.json()["max_batch_size"] == 100
    assert {"BR", "MX", "CO"}.issubset(catalog.json()["countries"])
    assert {"stripe", "adyen", "dlocal", "mercadopago"}.issubset(catalog.json()["providers"])
    assert {"PIX", "SPEI", "PSE", "CASH_IN_STORE"}.issubset(catalog.json()["payment_method_categories"])

    first = client.post("/v1/transaction-samples", json={"schema_version": "1.0", "count": 3, "seed": 42})
    second = client.post("/v1/transaction-samples", json={"schema_version": "1.0", "count": 3, "seed": 42})
    assert first.status_code == second.status_code == 200
    assert first.json()["transactions"] == second.json()["transactions"]
    assert "outcome" not in first.json()["transactions"][0]
    assert "status" not in first.json()["transactions"][0]


def test_batch_persists_before_202_and_can_be_read_back():
    response = _submit(_batch())
    assert response.status_code == 202
    accepted = response.json()
    assert accepted["status"] == "PROCESSING"
    assert len(accepted["transaction_ids"]) == 1

    transaction = client.get(f"/v1/transactions/{accepted['transaction_ids'][0]}")
    assert transaction.status_code == 200
    body = transaction.json()
    # The durable worker (TASK-TXN-WORKER-001) may already have driven this to a
    # terminal state by the time we read it back — persist-before-202 is what's
    # under test here, not how far the pipeline got.
    assert body["status"] in {"PROCESSING", "SUCCEEDED", "FAILED", "UNKNOWN"}
    if body["status"] == "PROCESSING":
        assert body["processing"]["stage"] in {"RECEIVED", "NORMALIZING", "CLASSIFYING", "AGGREGATING", "ANALYZING"}
    else:
        assert body["processing"] == {"stage": "COMPLETE", "progress_percent": 100, "failure_code": None}

    batch = client.get(f"/v1/transaction-batches/{accepted['batch_id']}")
    assert batch.status_code == 200
    assert [item["transaction_id"] for item in batch.json()["items"]] == accepted["transaction_ids"]


def test_idempotency_reuses_ids_and_rejects_conflicting_payload():
    payload = _batch("stable-key-0001")
    first = _submit(payload)
    second = _submit(deepcopy(payload))
    assert first.status_code == second.status_code == 202
    assert first.json()["transaction_ids"] == second.json()["transaction_ids"]

    conflicting = _submit(_batch("stable-key-0001", amount_minor=7990))
    assert conflicting.status_code == 409
    assert conflicting.json()["detail"] == "IDEMPOTENCY_KEY_CONFLICT"


def test_batch_rejects_non_facts_and_enforces_header_contract():
    invalid = _batch("invalid-facts-0001")
    invalid["transactions"][0]["status"] = "SUCCEEDED"
    assert _submit(invalid).status_code == 422

    missing_header = client.post("/v1/transaction-batches", json=_batch("missing-header-0001"))
    assert missing_header.status_code == 422

    too_many = _batch("too-many-items-0001")
    too_many["transactions"] = [_transaction() for _ in range(101)]
    assert _submit(too_many).status_code == 422


def test_concurrent_batch_submissions_do_not_corrupt_the_shared_connection():
    """Reproduces the real failure: DuckDB's single shared connection interleaving
    BEGIN/INSERT/COMMIT across FastAPI's threadpool without _BATCH_LOCK fails ~100%
    of the time under concurrent load."""

    def _submit_unique(index: int):
        return _submit(_batch(f"concurrent-key-{index:04d}"))

    with ThreadPoolExecutor(max_workers=20) as pool:
        responses = list(pool.map(_submit_unique, range(40)))

    assert [r.status_code for r in responses] == [202] * 40
    transaction_ids = {r.json()["transaction_ids"][0] for r in responses}
    assert len(transaction_ids) == 40


def test_admin_reset_requires_a_configured_matching_key_and_clears_transaction_projections(monkeypatch):
    accepted = _submit(_batch("reset-before-clear-0001"))
    assert accepted.status_code == 202

    endpoint = "/v1/admin/transaction-data/reset"
    confirmation = {"confirmation": "DELETE_SYNTHETIC_TRANSACTION_DATA"}
    assert client.post(endpoint, json=confirmation).status_code == 503

    monkeypatch.setattr(settings, "transaction_reset_key", "demo-reset-secret")
    assert client.post(endpoint, json=confirmation).status_code == 403
    assert client.post(endpoint, json={"confirmation": "no"}, headers={"X-Lumen-Admin-Key": "demo-reset-secret"}).status_code == 422

    reset = client.post(endpoint, json=confirmation, headers={"X-Lumen-Admin-Key": "demo-reset-secret"})
    assert reset.status_code == 200
    body = reset.json()
    assert body["schema_version"] == "1.0"
    assert body["removed"]["transaction_records"] == 1
    assert body["removed"]["transaction_batches"] == 1
    assert client.get("/v1/transactions").json()["items"] == []
    assert client.get(f"/v1/transaction-batches/{accepted.json()['batch_id']}").status_code == 404

    # Reset removes idempotency state too, so this represents a genuinely fresh demo workspace.
    after_reset = _submit(_batch("reset-before-clear-0001"))
    assert after_reset.status_code == 202
    assert after_reset.json()["batch_id"] != accepted.json()["batch_id"]
