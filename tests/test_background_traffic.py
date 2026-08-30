import inspect
from pathlib import Path
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.simulation.background_traffic import generate_background_transactions, submit_background_batch
from main import app


ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_generation_is_reproducible_and_omits_outcome_fields():
    seed_a, first = generate_background_transactions(5, seed=99)
    seed_b, second = generate_background_transactions(5, seed=99)
    assert seed_a == seed_b == 99
    assert first == second
    assert "status" not in first[0]
    assert "outcome" not in first[0]


@pytest.mark.parametrize("bad_count", [0, -1, 101])
def test_generation_rejects_out_of_range_count(bad_count):
    with pytest.raises(ValueError):
        generate_background_transactions(bad_count)


def test_harness_never_imports_ingestion_directly():
    import app.simulation.background_traffic as module

    source = inspect.getsource(module)
    assert "app.ingestion" not in source


def test_background_traffic_imports_in_a_fresh_process_without_api_cycle():
    completed = subprocess.run(
        [sys.executable, "-c", "import app.simulation.background_traffic; print('background import OK')"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert completed.stdout.strip() == "background import OK"


def test_submit_persists_then_worker_advances_it_to_a_terminal_state():
    response = submit_background_batch(3, seed=7)
    assert response["seed"] == 7
    assert len(response["transaction_ids"]) == 3

    batch = client.get(f"/v1/transaction-batches/{response['batch_id']}")
    assert batch.status_code == 200
    statuses = {item["status"] for item in batch.json()["items"]}
    assert statuses <= {"SUCCEEDED", "FAILED", "UNKNOWN"}


def test_background_batch_changes_metrics_only_after_worker_processing():
    assert client.get("/v1/metrics/current").json() == []

    response = submit_background_batch(3, seed=17)

    metrics = client.get("/v1/metrics/current")
    assert metrics.status_code == 200
    assert sum(item["eligible_attempts"] for item in metrics.json()) == len(response["transaction_ids"])


def test_endpoint_requires_demo_mode_then_accepts_request(monkeypatch):
    monkeypatch.setattr(settings, "demo_mode", False)
    denied = client.post("/demo/background-traffic", json={"count": 2})
    assert denied.status_code == 403

    monkeypatch.setattr(settings, "demo_mode", True)
    accepted = client.post("/demo/background-traffic", json={"count": 2, "seed": 123})
    assert accepted.status_code == 202
    assert accepted.json()["seed"] == 123


def test_endpoint_rejects_count_outside_bounds():
    settings.demo_mode = True
    try:
        response = client.post("/demo/background-traffic", json={"count": 0})
        assert response.status_code == 422
    finally:
        settings.demo_mode = False


def test_baseline_traffic_endpoint_requires_demo_mode_then_seeds_history(monkeypatch):
    monkeypatch.setattr(settings, "demo_mode", False)
    denied = client.post("/demo/baseline-traffic", json={"window_count": 2, "payments_per_window": 12})
    assert denied.status_code == 403

    monkeypatch.setattr(settings, "demo_mode", True)
    accepted = client.post("/demo/baseline-traffic", json={"window_count": 2, "payments_per_window": 12})
    assert accepted.status_code == 202
    body = accepted.json()
    assert body["source"] == "live_stream"
    assert body["window_count"] == 2
    assert body["payments_requested"] == 24
    assert body["events_published"] >= 24
