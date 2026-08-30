from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.benchmark.parquet import materialize_canonical_events, run_historical_parquet_benchmark
from app.ingestion import ingest_event, storage
from app.simulation import HistoricalTransactionGenerator, load_generator_config
from app.streaming import IngestionListener, TransactionServer

CONFIG_PATH = Path("config/generator/v1/default.json")
START = datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc)


def test_benchmark_uses_server_listener_then_exports_partitioned_parquet(tmp_path):
    report = run_historical_parquet_benchmark(
        load_generator_config(CONFIG_PATH),
        start_at=START,
        output_dir=tmp_path / "parquet",
        transactions_per_minute=2,
        batch_minutes=30,
        total_minutes=180,
    )

    parquet_files = tuple((tmp_path / "parquet").rglob("*.parquet"))
    assert report.generated_events == report.published_events == report.listener_consumed == report.accepted_events
    assert report.quarantined_events == 0
    assert report.parquet_rows == report.accepted_events
    assert report.parquet_partitions == len(parquet_files) == 1
    assert report.analyzed_windows > 0
    assert report.low_sample_events == 12
    assert report.peak_process_rss_bytes > 0
    assert all("event_date=2026-06-01" in path.as_posix() for path in parquet_files)


def test_benchmark_digest_is_reproducible_for_same_seed(tmp_path):
    config = load_generator_config(CONFIG_PATH)
    first = run_historical_parquet_benchmark(
        config,
        start_at=START,
        output_dir=tmp_path / "first",
        transactions_per_minute=2,
        total_minutes=120,
    )
    storage.reset_connection()
    second = run_historical_parquet_benchmark(
        config,
        start_at=START,
        output_dir=tmp_path / "second",
        transactions_per_minute=2,
        total_minutes=120,
    )

    assert first.event_digest == second.event_digest
    assert first.generated_events == second.generated_events
    assert first.parquet_rows == second.parquet_rows


def test_parquet_layout_accepts_schema_compatible_new_provider_combination(tmp_path, valid_attempt):
    valid_attempt["provider_id"] = "provider_future"
    server = TransactionServer()
    server.publish([valid_attempt])
    consumed = IngestionListener(server).consume_available()

    rows, partitions, _ = materialize_canonical_events(storage.get_connection(), tmp_path / "parquet")
    columns = storage.get_connection().execute(
        "DESCRIBE SELECT * FROM read_parquet(?)", [str(next((tmp_path / "parquet").rglob("*.parquet")))]
    ).fetchall()

    assert consumed.accepted == rows == 1
    assert partitions == 1
    assert {column[0] for column in columns} == {
        "event_id",
        "attempt_id",
        "payment_id",
        "event_time",
        "status",
        "is_late",
        "applied",
        "canonical_json",
        "event_date",
    }


def test_materialization_refuses_existing_output_directory(tmp_path):
    output_dir = tmp_path / "parquet"
    output_dir.mkdir()

    with pytest.raises(FileExistsError, match="already exists"):
        materialize_canonical_events(storage.get_connection(), output_dir)


def test_benchmark_refuses_storage_contaminated_by_an_earlier_run(tmp_path, valid_attempt):
    ingest_event(valid_attempt)

    with pytest.raises(RuntimeError, match="storage is not empty"):
        run_historical_parquet_benchmark(
            load_generator_config(CONFIG_PATH),
            start_at=START,
            output_dir=tmp_path / "parquet",
            transactions_per_minute=2,
            total_minutes=60,
        )
