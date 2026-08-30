import json
from datetime import timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from app.api.transactions import BatchRequest, TransactionInput, _create_batch, _record_from_row
from app.ingestion.storage import get_connection
from app.worker import transaction_worker as worker
from main import app

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "contracts" / "v1"


def _new_transaction_id(*, key: str) -> str:
    request = BatchRequest(
        schema_version="1.0",
        idempotency_key=key,
        transactions=[
            TransactionInput(
                merchant_id="merchant_br_01",
                provider_id="provider_alpha",
                issuer_bank="bank_br_a",
                country="BR",
                currency="BRL",
                amount_minor=12990,
                payment_method_category="CARD",
                card_brand="VISA",
                card_type="CREDIT",
                channel="WEB",
            )
        ],
    )
    response = _create_batch(request)
    return response["transaction_ids"][0]


def _record(transaction_id: str) -> dict:
    row = get_connection().execute(
        "SELECT status, processing_json, outcome_json, classification_json, updated_at "
        "FROM transaction_records WHERE transaction_id = ?",
        [transaction_id],
    ).fetchone()
    return {
        "status": row[0],
        "processing": json.loads(row[1]),
        "outcome": json.loads(row[2]) if row[2] else None,
        "classification": json.loads(row[3]) if row[3] else None,
        "updated_at": row[4],
    }


def test_worker_advances_one_stage_at_a_time_with_monotonic_progress():
    transaction_id = _new_transaction_id(key="worker-key-0001")
    seen_progress = [_record(transaction_id)["processing"]["progress_percent"]]

    for _ in range(len(worker.STAGE_ORDER) - 1):
        assert worker.advance_transaction(transaction_id) is True
        seen_progress.append(_record(transaction_id)["processing"]["progress_percent"])

    assert seen_progress == sorted(seen_progress)
    assert seen_progress[-1] == 100
    final = _record(transaction_id)
    assert final["status"] in {"SUCCEEDED", "FAILED", "UNKNOWN"}
    assert final["processing"]["stage"] == "COMPLETE"


def test_crash_between_stages_resumes_from_persisted_stage_not_from_scratch():
    transaction_id = _new_transaction_id(key="worker-key-0002")
    worker.advance_transaction(transaction_id)
    worker.advance_transaction(transaction_id)
    mid_flight = _record(transaction_id)
    assert mid_flight["processing"]["stage"] == "CLASSIFYING"

    worker.run_to_completion(transaction_id)

    final = _record(transaction_id)
    assert final["processing"]["stage"] == "COMPLETE"
    assert final["processing"]["progress_percent"] == 100


def test_duplicate_delivery_does_not_reprocess_a_terminal_transaction():
    transaction_id = _new_transaction_id(key="worker-key-0003")
    worker.run_to_completion(transaction_id)
    terminal = _record(transaction_id)

    worker.run_to_completion(transaction_id)
    worker.advance_transaction(transaction_id)

    assert _record(transaction_id) == terminal


def test_lease_prevents_a_second_worker_from_advancing_the_same_transaction():
    transaction_id = _new_transaction_id(key="worker-key-0004")
    con = get_connection()
    assert worker._acquire_lease(con, transaction_id, "worker-a", worker.DEFAULT_LEASE_SECONDS)
    before = _record(transaction_id)

    assert worker.advance_transaction(transaction_id, worker_id="worker-b") is False
    assert _record(transaction_id) == before


def test_agent_suggestion_job_runs_after_the_duckdb_lock_is_released(monkeypatch):
    events: list[str] = []

    class RecordingLock:
        def __enter__(self):
            events.append("lock-enter")

        def __exit__(self, exc_type, exc, traceback):
            events.append("lock-exit")

    monkeypatch.setattr(worker, "CONNECTION_LOCK", RecordingLock())
    monkeypatch.setattr(worker, "_acquire_lease", lambda *args: True)
    monkeypatch.setattr(
        worker,
        "_advance_locked",
        lambda *args: (events.append("advance"), [("persisted-incident", {"PROVIDER_TIMEOUT": 1})])[1],
    )
    monkeypatch.setattr(
        worker,
        "_suggest_for_persisted_incident",
        lambda *args: events.append("suggest"),
    )

    assert worker.advance_transaction("txn_post_commit") is True
    assert events == ["lock-enter", "advance", "lock-exit", "suggest"]


def test_expired_lease_is_reclaimable_by_reconciliation():
    transaction_id = _new_transaction_id(key="worker-key-0005")
    con = get_connection()
    stale_expiry = worker._now() - timedelta(seconds=10)
    con.execute(
        "UPDATE transaction_records SET lease_owner = ?, lease_expires_at = ? WHERE transaction_id = ?",
        ["stale-worker", stale_expiry, transaction_id],
    )

    resumed = worker.reconcile_stuck()

    assert resumed >= 1
    assert _record(transaction_id)["status"] != "PROCESSING"


def test_pipeline_failure_never_becomes_a_business_decline(monkeypatch):
    transaction_id = _new_transaction_id(key="worker-key-0006")

    def _boom(_transaction_id: str, _input: dict, _correlation_id: str):
        raise RuntimeError("simulated provider adapter crash")

    monkeypatch.setattr(worker, "_generate_outcome", _boom)
    worker.run_to_completion(transaction_id)

    final = _record(transaction_id)
    assert final["status"] == "UNKNOWN"
    assert final["processing"]["stage"] == "PIPELINE_FAILED"
    assert final["processing"]["progress_percent"] == 100
    assert final["processing"]["failure_code"] == "WORKER_ERROR:RuntimeError"
    assert final["outcome"] is None
    assert final["classification"] is None


def test_analytics_failure_rolls_back_canonical_and_incident_side_effects(monkeypatch):
    transaction_id = _new_transaction_id(key="worker-key-analytics-rollback")

    def _boom(_con, _correlation_id: str):
        raise RuntimeError("simulated analytics failure")

    monkeypatch.setattr(worker, "derive_incidents_for_correlation", _boom)
    worker.run_to_completion(transaction_id)

    final = _record(transaction_id)
    assert final["status"] == "UNKNOWN"
    assert final["processing"]["stage"] == "PIPELINE_FAILED"
    con = get_connection()
    assert con.execute("SELECT count(*) FROM canonical_events WHERE event_id = ?", [f"evt_{transaction_id}"]).fetchone()[0] == 0
    assert con.execute("SELECT count(*) FROM transaction_incident_links WHERE transaction_id = ?", [transaction_id]).fetchone()[0] == 0


def test_outcome_generation_is_deterministic_for_the_same_transaction_id():
    transaction = {
        "merchant_id": "merchant_br_01",
        "provider_id": "provider_alpha",
        "issuer_bank": "bank_br_a",
        "country": "BR",
        "currency": "BRL",
        "amount_minor": 12990,
        "payment_method_category": "CARD",
        "card_brand": "VISA",
        "card_type": "CREDIT",
    }
    assert worker._generate_outcome("txn_fixed_id_for_determinism", transaction, "corr_fixed") == worker._generate_outcome(
        "txn_fixed_id_for_determinism", transaction, "corr_fixed"
    )


def test_worker_persists_one_canonical_event_derived_from_the_public_input():
    transaction_id = _new_transaction_id(key="worker-key-adapter-event")
    worker.run_to_completion(transaction_id)
    worker.run_to_completion(transaction_id)

    rows = get_connection().execute(
        "SELECT canonical_json FROM canonical_events WHERE event_id = ?", [f"evt_{transaction_id}"]
    ).fetchall()
    assert len(rows) == 1
    event = json.loads(rows[0][0])
    assert event["merchant_id"] == "merchant_br_01"
    assert event["amount_minor"] == 12990


def _record_schema_validator() -> Draft202012Validator:
    schemas = [json.loads(path.read_text(encoding="utf-8")) for path in SCHEMAS_DIR.glob("*.schema.json")]
    registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas if "$id" in s)
    schema = json.loads((SCHEMAS_DIR / "transaction-record.schema.json").read_text(encoding="utf-8"))
    return Draft202012Validator(schema, registry=registry)


def test_terminal_records_validate_against_ctr_txl_001_schema():
    validator = _record_schema_validator()
    _RECORD_COLUMNS = (
        "transaction_id, batch_id, created_at, updated_at, status, input_json, "
        "processing_json, outcome_json, classification_json, correlation_id"
    )
    seen_statuses = set()
    for index in range(12):
        transaction_id = _new_transaction_id(key=f"worker-schema-key-{index:04d}")
        worker.run_to_completion(transaction_id)
        row = get_connection().execute(
            f"SELECT {_RECORD_COLUMNS} FROM transaction_records WHERE transaction_id = ?", [transaction_id]
        ).fetchone()
        instance = _record_from_row(row)
        seen_statuses.add(instance["status"])
        errors = list(validator.iter_errors(instance))
        assert not errors, errors
    assert seen_statuses <= {"SUCCEEDED", "FAILED", "UNKNOWN"}


def test_internal_scenario_effects_do_not_leak_from_a_terminal_record():
    transaction_id = _new_transaction_id(key="worker-scenario-effects-contract")
    get_connection().execute(
        "UPDATE transaction_records SET input_json = ? WHERE transaction_id = ?",
        [
            json.dumps(
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
                    "scenario_effects": {"timeout_rate": 1.0},
                }
            ),
            transaction_id,
        ],
    )
    worker.run_to_completion(transaction_id)
    row = get_connection().execute(
        "SELECT transaction_id, batch_id, created_at, updated_at, status, input_json, processing_json, outcome_json, classification_json, correlation_id "
        "FROM transaction_records WHERE transaction_id = ?",
        [transaction_id],
    ).fetchone()

    assert "scenario_effects" not in _record_from_row(row)["input"]


def test_transaction_batch_reaches_terminal_state_via_background_worker():
    client = TestClient(app)
    payload = {
        "schema_version": "1.0",
        "idempotency_key": "worker-endpoint-key-0001",
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
    response = client.post(
        "/v1/transaction-batches", json=payload, headers={"Idempotency-Key": payload["idempotency_key"]}
    )
    assert response.status_code == 202
    transaction_id = response.json()["transaction_ids"][0]

    detail = client.get(f"/v1/transactions/{transaction_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["processing"] == {"stage": "COMPLETE", "progress_percent": 100, "failure_code": None}
    assert body["status"] in {"SUCCEEDED", "FAILED", "UNKNOWN"}
