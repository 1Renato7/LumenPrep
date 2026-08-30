"""TASK-DATA-005: materialize accepted canonical events as partitioned Parquet.

The benchmark intentionally uses the same internal data path as the application:
generator -> transaction server -> ingestion listener -> DuckDB -> aggregation.
It never exports a generator batch directly, which keeps validation, deduplication
and ordering in the measurement.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
import sys
from typing import Any

from app.aggregation import compute_windows
from app.ingestion.storage import get_connection
from app.simulation import HistoricalTransactionGenerator, load_generator_config
from app.simulation.config import GeneratorConfig
from app.streaming import IngestionListener, TransactionServer


@dataclass(frozen=True)
class BenchmarkReport:
    """Evidence emitted by a completed deterministic benchmark run."""

    seed: int
    config_fingerprint: str
    start_at: str
    horizon_minutes: int
    transactions_per_minute: float
    batch_minutes: int
    generated_events: int
    published_events: int
    listener_consumed: int
    accepted_events: int
    quarantined_events: int
    analyzed_windows: int
    low_sample_events: int
    parquet_rows: int
    parquet_partitions: int
    parquet_bytes: int
    event_digest: str
    duration_seconds: float
    peak_process_rss_bytes: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        """Produce a concise, commit-friendly report with measured run evidence."""

        return "\n".join(
            (
                "# Benchmark TASK-DATA-005",
                "",
                "| Campo | Valor |",
                "| --- | --- |",
                f"| Seed | `{self.seed}` |",
                f"| Config fingerprint | `{self.config_fingerprint}` |",
                f"| Início UTC | `{self.start_at}` |",
                f"| Horizonte | `{self.horizon_minutes}` min |",
                f"| Taxa configurada | `{self.transactions_per_minute:g}` transações/min |",
                f"| Eventos gerados / publicados / aceitos | `{self.generated_events}` / `{self.published_events}` / `{self.accepted_events}` |",
                f"| Listener consumiu / quarantined | `{self.listener_consumed}` / `{self.quarantined_events}` |",
                f"| Janelas analisadas | `{self.analyzed_windows}` |",
                f"| Eventos na janela de baixa amostra | `{self.low_sample_events}` |",
                f"| Linhas / partições / bytes Parquet | `{self.parquet_rows}` / `{self.parquet_partitions}` / `{self.parquet_bytes}` |",
                f"| Duração | `{self.duration_seconds:.3f}` s |",
                f"| Pico RSS do processo | `{self.peak_process_rss_bytes}` bytes |",
                f"| Digest determinístico dos eventos | `{self.event_digest}` |",
                "",
                "## Limitações",
                "",
                "- O RSS mede o processo inteiro, incluindo a memória nativa do DuckDB; ele também inclui o runtime Python e não separa cada componente.",
                "- O adaptador local `TransactionServer` mantém seu log durante o run; esta medição inclui esse custo do caminho atual.",
                "- O dataset contém apenas eventos canônicos aceitos pelo listener; configurações internas e ground truth não são exportados.",
                "",
            )
        )


def materialize_canonical_events(connection: Any, output_dir: Path) -> tuple[int, int, int]:
    """Export accepted canonical events as date-partitioned Parquet without overwrite.

    Refusing an existing output directory prevents a benchmark rerun from silently
    mixing data from different seeds or configurations.
    """

    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"Parquet output directory already exists: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    path_literal = _sql_literal(output_dir.resolve().as_posix())
    connection.execute(
        f"""
        COPY (
            SELECT
                event_id,
                attempt_id,
                payment_id,
                event_time,
                status,
                is_late,
                applied,
                canonical_json,
                CAST(event_time AS DATE) AS event_date
            FROM canonical_events
            ORDER BY event_time, event_id
        ) TO {path_literal} (FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY (event_date))
        """
    )
    parquet_files = tuple(output_dir.rglob("*.parquet"))
    rows = sum(_parquet_row_count(connection, item) for item in parquet_files)
    return rows, len(parquet_files), sum(item.stat().st_size for item in parquet_files)


def run_historical_parquet_benchmark(
    config: GeneratorConfig,
    *,
    start_at: datetime,
    output_dir: Path,
    transactions_per_minute: float,
    batch_minutes: int = 60,
    total_minutes: int | None = None,
) -> BenchmarkReport:
    """Run the production-shaped internal pipeline and materialize its accepted data."""

    if transactions_per_minute <= 0:
        raise ValueError("transactions_per_minute must be positive")
    if batch_minutes <= 0:
        raise ValueError("batch_minutes must be positive")

    horizon_minutes = total_minutes if total_minutes is not None else config.days * 24 * 60
    if horizon_minutes <= 0 or horizon_minutes > config.days * 24 * 60:
        raise ValueError("total_minutes must be within the configured historical horizon")

    generator = HistoricalTransactionGenerator(config, start_at=start_at)
    server = TransactionServer()
    listener = IngestionListener(server)
    connection = get_connection()
    _require_empty_ingestion_storage(connection)
    generated_events = published_events = listener_consumed = accepted_events = quarantined_events = 0

    started = perf_counter()
    peak_process_rss_bytes = _process_rss_bytes()
    for batch in generator.iter_batches(
        transactions_per_minute=transactions_per_minute,
        batch_minutes=batch_minutes,
        total_minutes=horizon_minutes,
    ):
        receipt = server.publish(batch.events)
        report = listener.consume_available(limit=len(batch.events) or 1)
        generated_events += len(batch.events)
        published_events += receipt.accepted
        listener_consumed += report.consumed
        accepted_events += report.accepted
        quarantined_events += report.quarantined
        peak_process_rss_bytes = max(peak_process_rss_bytes, _process_rss_bytes())

    analyzed_windows = len(compute_windows(connection))
    parquet_rows, parquet_partitions, parquet_bytes = materialize_canonical_events(connection, output_dir)
    low_sample_at = start_at.astimezone(timezone.utc).replace(second=0, microsecond=0)
    low_sample_at = low_sample_at.replace() + _minutes(horizon_minutes // 2)
    low_sample_events = connection.execute(
        "SELECT count(*) FROM canonical_events WHERE date_trunc('minute', event_time) = ?",
        [low_sample_at.replace(tzinfo=None)],
    ).fetchone()[0]
    event_digest = _canonical_event_digest(connection)
    peak_process_rss_bytes = max(peak_process_rss_bytes, _process_rss_bytes())
    duration_seconds = perf_counter() - started

    return BenchmarkReport(
        seed=config.seed,
        config_fingerprint=config.fingerprint,
        start_at=_iso_z(start_at),
        horizon_minutes=horizon_minutes,
        transactions_per_minute=transactions_per_minute,
        batch_minutes=batch_minutes,
        generated_events=generated_events,
        published_events=published_events,
        listener_consumed=listener_consumed,
        accepted_events=accepted_events,
        quarantined_events=quarantined_events,
        analyzed_windows=analyzed_windows,
        low_sample_events=low_sample_events,
        parquet_rows=parquet_rows,
        parquet_partitions=parquet_partitions,
        parquet_bytes=parquet_bytes,
        event_digest=event_digest,
        duration_seconds=duration_seconds,
        peak_process_rss_bytes=peak_process_rss_bytes,
    )


def write_benchmark_report(report: BenchmarkReport, report_path: Path) -> None:
    """Write JSON plus Markdown evidence; refusing overwrite preserves prior evidence."""

    report_path = Path(report_path)
    if report_path.exists():
        raise FileExistsError(f"Benchmark report already exists: {report_path}")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report.to_markdown(), encoding="utf-8")
    report_path.with_suffix(".json").write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _canonical_event_digest(connection: Any) -> str:
    digest = sha256()
    for event_id, canonical_json in connection.execute(
        "SELECT event_id, canonical_json FROM canonical_events ORDER BY event_id"
    ).fetchall():
        digest.update(event_id.encode("utf-8"))
        digest.update(b"\0")
        digest.update(canonical_json.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _require_empty_ingestion_storage(connection: Any) -> None:
    """Refuse to benchmark over facts from an earlier run.

    A benchmark result is only comparable when every exported row originated
    from the configured generator run.  The caller may point ``DUCKDB_PATH``
    at a new database instead of risking a destructive reset of application
    data.
    """

    raw_events, canonical_events, quarantined_events = connection.execute(
        "SELECT "
        "(SELECT count(*) FROM raw_events), "
        "(SELECT count(*) FROM canonical_events), "
        "(SELECT count(*) FROM quarantine)"
    ).fetchone()
    if raw_events or canonical_events or quarantined_events:
        raise RuntimeError(
            "benchmark storage is not empty; set DUCKDB_PATH to a new database before running"
        )


def _parquet_row_count(connection: Any, path: Path) -> int:
    return connection.execute(f"SELECT count(*) FROM read_parquet({_sql_literal(path.as_posix())})").fetchone()[0]


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _minutes(value: int):
    from datetime import timedelta

    return timedelta(minutes=value)


def _process_rss_bytes() -> int:
    """Return the process working-set peak without instrumentation overhead."""

    if sys.platform == "win32":
        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        process = ctypes.windll.kernel32.GetCurrentProcess()
        get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
        get_process_memory_info.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(ProcessMemoryCounters),
            wintypes.DWORD,
        ]
        get_process_memory_info.restype = wintypes.BOOL
        if get_process_memory_info(process, ctypes.byref(counters), counters.cb):
            return int(counters.PeakWorkingSetSize)
        return 0

    import resource

    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _parse_start_at(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("start-at must include a timezone")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Run TASK-DATA-005 and materialize partitioned Parquet.")
    parser.add_argument("--config", type=Path, default=Path("config/generator/v1/default.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument(
        "--start-at",
        type=_parse_start_at,
        default=_parse_start_at("2026-06-01T00:00:00Z"),
    )
    parser.add_argument("--transactions-per-minute", type=float, default=0.1)
    parser.add_argument("--batch-minutes", type=int, default=60)
    parser.add_argument("--total-minutes", type=int)
    args = parser.parse_args()
    # The DuckDB path is configured before import through DUCKDB_PATH.  Create
    # only its parent; the Parquet destination itself must stay absent so the
    # materializer can reject accidental overwrite.
    args.output_dir.parent.mkdir(parents=True, exist_ok=True)

    report = run_historical_parquet_benchmark(
        load_generator_config(args.config),
        start_at=args.start_at,
        output_dir=args.output_dir,
        transactions_per_minute=args.transactions_per_minute,
        batch_minutes=args.batch_minutes,
        total_minutes=args.total_minutes,
    )
    write_benchmark_report(report, args.report)
    print(json.dumps(report.as_dict(), sort_keys=True))


if __name__ == "__main__":
    main()
