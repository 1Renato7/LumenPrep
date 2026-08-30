import json
from datetime import datetime, timezone
from pathlib import Path

from app.simulation import LiveStreamController, ScenarioV1Contract, load_generator_config
from app.streaming import TransactionServer, get_ingestion_listener, get_transaction_server
from app.streaming.listener import IngestionListener

CONFIG_PATH = Path("config/generator/v1/default.json")
SCHEMA_PATH = Path("contracts/v1/scenario.schema.json")
FIXTURE_PATH = Path("contracts/fixtures/scenario-provider-br.json")


def _controller() -> LiveStreamController:
    config = load_generator_config(CONFIG_PATH)
    return LiveStreamController(
        config,
        get_transaction_server(),
        reference_time=datetime(2026, 8, 29, 14, 0, 0, tzinfo=timezone.utc),
    )


def _scenario():
    contract = ScenarioV1Contract(SCHEMA_PATH)
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return contract.parse(payload)


def test_baseline_batch_is_published_then_consumed_by_listener():
    controller = _controller()
    published = controller.emit_baseline_batch(20)
    assert published > 0
    report = get_ingestion_listener().consume_available()
    assert report.consumed == published
    assert report.accepted == published


def test_baseline_history_spans_consecutive_windows_with_shared_window_correlation():
    server = TransactionServer()
    config = load_generator_config(CONFIG_PATH)
    controller = LiveStreamController(
        config,
        server,
        reference_time=datetime(2026, 8, 29, 14, 2, 0, tzinfo=timezone.utc),
    )

    result = controller.seed_baseline_history(window_count=3, payments_per_window=12)
    events = [item.payload for item in server.read_after(0, limit=500)]

    assert result.payments_requested == 36
    assert result.events_published == len(events)
    assert result.first_window_start == "2026-08-29T14:00:00Z"
    assert result.last_window_end == "2026-08-29T14:15:00Z"
    correlations = {str(event["correlation_id"]) for event in events}
    assert correlations == {
        "demo:baseline:1788012000",
        "demo:baseline:1788012300",
        "demo:baseline:1788012600",
    }
    timestamps = [str(event["event_time"]) for event in events]
    assert min(timestamps) >= result.first_window_start
    assert max(timestamps) < result.last_window_end


def test_inject_scenario_degrades_only_matching_attempts():
    controller = _controller()
    scenario = _scenario()

    result = controller.inject_scenario(scenario, payment_count=80)

    assert result.scenario_id == "scenario_provider_br"
    assert result.correlation_id == "demo:scenario_provider_br"
    assert result.matched_attempts > 0
    assert result.events_published >= result.matched_attempts
    assert get_ingestion_listener().consume_available(limit=500).accepted == result.events_published


def test_injected_scenario_measurably_lowers_approval_rate():
    """approval_rate_multiplier=0.55 no fixture deve reduzir SUCCEEDED entre
    as tentativas que casam o filtro, comparado ao baseline (~0.87 stripe/BR)."""
    controller = _controller()
    scenario = _scenario()

    from app.aggregation import get_current_metrics

    controller.inject_scenario(scenario, payment_count=150)
    get_ingestion_listener().consume_available(limit=500)
    windows = get_current_metrics(dimensions={"provider_id": "stripe", "country": "BR"})
    assert windows
    approval_rate = sum(w.approval_rate * w.eligible_attempts for w in windows) / sum(w.eligible_attempts for w in windows)
    assert approval_rate < 0.75


def test_seeded_history_makes_the_next_scenario_eligible_for_detection():
    from app.aggregation import get_current_metrics
    from app.detection import detect_candidates

    server = TransactionServer()
    listener = IngestionListener(server)
    config = load_generator_config(CONFIG_PATH)
    controller = LiveStreamController(
        config,
        server,
        reference_time=datetime(2026, 8, 29, 14, 0, 0, tzinfo=timezone.utc),
    )
    controller.seed_baseline_history(window_count=4, payments_per_window=100)
    while listener.consume_available(limit=500).consumed:
        pass

    result = controller.inject_scenario(_scenario(), payment_count=300)
    while listener.consume_available(limit=500).consumed:
        pass

    candidates = detect_candidates(get_current_metrics(), low_sample_attempts=config.low_sample_attempts)
    assert any(
        candidate.correlation_id == result.correlation_id
        and candidate.slice.get("provider_id") == "stripe"
        and candidate.slice.get("country") == "BR"
        for candidate in candidates
    )
