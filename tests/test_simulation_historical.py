from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from app.simulation import HistoricalTransactionGenerator, load_generator_config
from app.streaming import IngestionListener, TransactionServer

CONFIG_PATH = Path("config/generator/v1/default.json")
START = datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc)


def _events(*, total_minutes: int, rate: int) -> list[dict]:
    generator = HistoricalTransactionGenerator(load_generator_config(CONFIG_PATH), start_at=START)
    return [event for batch in generator.iter_batches(transactions_per_minute=rate, total_minutes=total_minutes) for event in batch.events]


def test_historical_generation_is_reproducible_with_the_same_seed():
    first = _events(total_minutes=180, rate=8)
    second = _events(total_minutes=180, rate=8)

    assert first == second
    assert first
    assert all(event["event_time"].endswith("Z") for event in first)


def test_historical_generation_has_hourly_seasonality_and_low_sample_window():
    events = _events(total_minutes=24 * 60, rate=25)
    by_minute = Counter(event["event_time"][:16] for event in events)
    by_hour = Counter(event["event_time"][11:13] for event in events)

    assert by_minute["2026-06-01T12:00"] == 12
    assert by_hour["13"] > by_hour["02"]


def test_historical_generator_publishes_without_importing_ingestion():
    server = TransactionServer()
    generator = HistoricalTransactionGenerator(load_generator_config(CONFIG_PATH), start_at=START)

    report = generator.publish(server, transactions_per_minute=4, total_minutes=45, batch_minutes=15)
    consumed = IngestionListener(server).consume_available(limit=500)

    assert report.generated_events == report.published_events == consumed.consumed
    assert consumed.accepted == report.generated_events
    source = Path("app/simulation/historical.py").read_text(encoding="utf-8")
    assert "app.ingestion" not in source
