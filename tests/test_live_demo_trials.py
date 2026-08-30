from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app.agent import DiagnosticSuggestionRepository
from app.config import settings
from app.ingestion import storage
from app.simulation.live_demo_trials import launch_trial, trial_catalog
from app.worker.transaction_worker import run_batch_to_completion
from main import app


@pytest.fixture
def isolated_trial_store(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "duckdb_path", str(tmp_path / "live-demo-trials.duckdb"))
    monkeypatch.setattr(settings, "openai_api_key", None)
    storage.reset_connection()
    try:
        yield storage.get_connection()
    finally:
        storage.reset_connection()


def test_catalog_has_only_the_two_fixed_25_transaction_trials():
    assert [(item["trial_id"], item["flow"], item["transaction_count"]) for item in trial_catalog()] == [
        ("deterministic", "DETERMINISTIC", 25),
        ("graph_enriched", "GRAPH_ENRICHED", 25),
    ]


def test_live_trial_routes_are_explicitly_gated(monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr(settings, "demo_live_trials_enabled", False)
    monkeypatch.setattr(settings, "demo_mode", False)
    disabled = client.get("/v1/demo/live-trials")
    assert disabled.status_code == 200
    assert disabled.json()["enabled"] is False
    assert disabled.json()["reason"] == "LIVE_DEMO_TRIALS_DISABLED"
    assert client.post("/v1/demo/live-trials/deterministic", headers={"Idempotency-Key": "demo-key-001"}).status_code == 403

    monkeypatch.setattr(settings, "demo_live_trials_enabled", True)
    monkeypatch.setattr(settings, "demo_mode", True)
    fixture_mode = client.get("/v1/demo/live-trials")
    assert fixture_mode.status_code == 200
    assert fixture_mode.json()["enabled"] is False
    assert fixture_mode.json()["reason"] == "LIVE_INCIDENTS_REQUIRE_DEMO_MODE_FALSE"

    monkeypatch.setattr(settings, "demo_mode", False)
    enabled = client.get("/v1/demo/live-trials")
    assert enabled.status_code == 200
    assert enabled.json()["enabled"] is True
    assert [trial["trial_id"] for trial in enabled.json()["trials"]] == ["deterministic", "graph_enriched"]
    assert client.post("/v1/demo/live-trials/unknown", headers={"Idempotency-Key": "demo-key-001"}).status_code == 422


@pytest.mark.parametrize("trial_id", ["deterministic", "graph_enriched"])
def test_each_trial_builds_an_idempotent_baseline_and_one_incident(isolated_trial_store, trial_id):
    first = launch_trial(trial_id, idempotency_key=f"trial-test-key-{trial_id}")
    second = launch_trial(trial_id, idempotency_key=f"trial-test-key-{trial_id}")

    assert first["batch_id"] == second["batch_id"]
    assert first["baseline_batch_ids"] == second["baseline_batch_ids"]
    assert len(first["baseline_batch_ids"]) == 1
    assert len(first["transaction_ids"]) == 25

    run_batch_to_completion(str(first["batch_id"]), derive_incidents_once_after_batch=True)
    rows = isolated_trial_store.execute(
        "SELECT input_json, status, outcome_json FROM transaction_records WHERE batch_id = ? ORDER BY batch_position",
        [first["batch_id"]],
    ).fetchall()
    assert len(rows) == 25
    failure_code = "insufficient_funds" if trial_id == "deterministic" else "do_not_honor"
    assert [json.loads(row[0])["provider_response_code"] for row in rows].count("approved") == 5
    assert [json.loads(row[0])["provider_response_code"] for row in rows].count(failure_code) == 20
    assert [row[1] for row in rows].count("SUCCEEDED") == 5
    assert [row[1] for row in rows].count("FAILED") == 20
    assert [json.loads(row[2])["provider_response_code"] for row in rows].count("approved") == 5
    assert [json.loads(row[2])["provider_response_code"] for row in rows].count(failure_code) == 20

    incidents = isolated_trial_store.execute(
        "SELECT incident_id FROM incident_records WHERE correlation_id = ?",
        [first["correlation_id"]],
    ).fetchall()
    assert len(incidents) == 1


def test_graph_trial_recovers_the_seeded_precedent_after_its_incident(isolated_trial_store):
    launched = launch_trial("graph_enriched", idempotency_key="trial-test-key-graph-retrieval")
    run_batch_to_completion(str(launched["batch_id"]), derive_incidents_once_after_batch=True)
    incident_id = isolated_trial_store.execute(
        "SELECT incident_id FROM incident_records WHERE correlation_id = ?",
        [launched["correlation_id"]],
    ).fetchone()[0]
    suggestion = DiagnosticSuggestionRepository().latest_for_incident(incident_id)
    assert suggestion is not None
    assert suggestion.retrieval_trace["status"] == "MATCH_FOUND"
    assert any(source["source"] == "incident_memory" for source in suggestion.retrieval_trace["sources"])
