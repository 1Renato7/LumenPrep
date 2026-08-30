"""CTR-STR-001 v1: a replaceable transaction-server adapter.

The MVP adapter deliberately keeps a bounded-in-process log.  It models the
same producer/server/listener boundary used by an external broker without
making demo execution depend on credentials or infrastructure.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Protocol


@dataclass(frozen=True)
class PublishedTransaction:
    sequence: int
    published_at: str
    payload: dict[str, object]


@dataclass(frozen=True)
class PublishReceipt:
    accepted: int
    first_sequence: int | None
    last_sequence: int | None


class TransactionPublisher(Protocol):
    """Producer-facing surface. It intentionally knows nothing about ingestion."""

    def publish(self, events: Iterable[Mapping[str, object]]) -> PublishReceipt: ...


class TransactionServer:
    """Append-only, sequence-addressable server for canonical transaction events."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._events: list[PublishedTransaction] = []
        self._next_sequence = 1

    def publish(self, events: Iterable[Mapping[str, object]]) -> PublishReceipt:
        accepted: list[PublishedTransaction] = []
        with self._lock:
            for event in events:
                if not isinstance(event, Mapping):
                    raise TypeError("CTR-STR-001 payload must be a mapping")
                envelope = PublishedTransaction(
                    sequence=self._next_sequence,
                    published_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    payload=deepcopy(dict(event)),
                )
                self._events.append(envelope)
                accepted.append(envelope)
                self._next_sequence += 1
        return PublishReceipt(
            accepted=len(accepted),
            first_sequence=accepted[0].sequence if accepted else None,
            last_sequence=accepted[-1].sequence if accepted else None,
        )

    def read_after(self, sequence: int, *, limit: int = 100) -> tuple[PublishedTransaction, ...]:
        if sequence < 0:
            raise ValueError("sequence must be non-negative")
        if limit <= 0:
            raise ValueError("limit must be positive")
        with self._lock:
            # Sequence starts at one and the backing log never compacts in the
            # MVP, so the index is stable and avoids an O(n) scan per poll.
            return tuple(self._events[sequence : sequence + limit])

    def health(self) -> dict[str, int]:
        with self._lock:
            return {"published": len(self._events), "last_sequence": self._next_sequence - 1}
