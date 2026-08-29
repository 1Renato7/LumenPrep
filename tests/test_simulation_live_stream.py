import json
from datetime import datetime, timezone
from pathlib import Path

from app.simulation import LiveStreamController, ScenarioV1Contract, load_generator_config

CONFIG_PATH = Path("config/generator/v1/default.json")
SCHEMA_PATH = Path("contracts/v1/scenario.schema.json")
FIXTURE_PATH = Path("contracts/fixtures/scenario-provider-br.json")


def _controller() -> LiveStreamController:
    config = load_generator_config(CONFIG_PATH)
    return LiveStreamController(config, reference_time=datetime(2026, 8, 29, 14, 0, 0, tzinfo=timezone.utc))


def _scenario():
    contract = ScenarioV1Contract(SCHEMA_PATH)
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return contract.parse(payload)


def test_baseline_batch_all_accepted():
    controller = _controller()
    results = controller.emit_baseline_batch(20)
    assert results
    assert all(r.status == "ACCEPTED" for r in results)


def test_inject_scenario_degrades_only_matching_attempts():
    controller = _controller()
    scenario = _scenario()

    result = controller.inject_scenario(scenario, payment_count=80)

    assert result.scenario_id == "scenario_provider_br"
    assert result.correlation_id == "demo:scenario_provider_br"
    assert result.matched_attempts > 0
    assert result.events_ingested >= result.matched_attempts
    assert result.accepted + result.quarantined == result.events_ingested


def test_injected_scenario_measurably_lowers_approval_rate():
    """approval_rate_multiplier=0.55 no fixture deve reduzir SUCCEEDED entre
    as tentativas que casam o filtro, comparado ao baseline (~0.87 stripe/BR)."""
    controller = _controller()
    scenario = _scenario()

    from app.aggregation import get_current_metrics

    controller.inject_scenario(scenario, payment_count=150)
    windows = get_current_metrics(dimensions={"provider_id": "stripe", "country": "BR"})
    assert windows
    approval_rate = sum(w.approval_rate * w.eligible_attempts for w in windows) / sum(w.eligible_attempts for w in windows)
    assert approval_rate < 0.75
