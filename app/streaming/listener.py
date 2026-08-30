"""The CMP-ING-001 side of CTR-STR-001.

Only this listener imports the ingestion boundary. Producers can therefore be
run in-process for the demo or moved to another process without coupling to
DuckDB, validation, deduplication, or aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Event, Thread
from time import sleep

from app.ingestion import IngestResult, ingest_events
from app.streaming.server import TransactionServer


@dataclass(frozen=True)
class ConsumeReport:
    consumed: int
    accepted: int
    duplicates: int
    quarantined: int
    cursor: int


class IngestionListener:
    def __init__(self, server: TransactionServer) -> None:
        self._server = server
        self._cursor = 0

    @property
    def cursor(self) -> int:
        return self._cursor

    def consume_available(self, *, limit: int = 100) -> ConsumeReport:
        envelopes = self._server.read_after(self._cursor, limit=limit)
        # Do not advance the cursor when the ingestion boundary itself raises:
        # the complete transaction rolls back and retrying the same event IDs
        # remains safe through the existing dedupe rule.
        results: tuple[IngestResult, ...] = ingest_events([envelope.payload for envelope in envelopes])
        for envelope in envelopes:
            self._cursor = envelope.sequence
        return ConsumeReport(
            consumed=len(results),
            accepted=sum(result.status == "ACCEPTED" for result in results),
            duplicates=sum(result.status == "DUPLICATE" for result in results),
            quarantined=sum(result.status == "QUARANTINED" for result in results),
            cursor=self._cursor,
        )


class IngestionListenerWorker:
    """Continuous listener used by the FastAPI runtime; tests can poll directly."""

    def __init__(self, listener: IngestionListener, *, poll_seconds: float = 0.05) -> None:
        self._listener = listener
        self._poll_seconds = poll_seconds
        self._stop = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if self._thread is None:
            self._thread = Thread(target=self._run, name="lumen-transaction-listener", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1)

    def _run(self) -> None:
        while not self._stop.is_set():
            report = self._listener.consume_available()
            if report.consumed == 0:
                sleep(self._poll_seconds)
