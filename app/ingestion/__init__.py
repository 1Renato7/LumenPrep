"""CMP-ING-001 — expõe ingest_event, IngestResult. TASK-ING-001..004."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel

from . import dedupe, ordering, storage
from .normalize import normalize
from .validate import validate_canonical


class IngestResult(BaseModel):
    status: Literal["ACCEPTED", "DUPLICATE", "QUARANTINED"]
    event_id: str
    canonical: dict | None = None
    errors: list[str] = []
    applied_to_current_state: bool = True


def _parse_dt(value: str) -> datetime:
    """DuckDB TIMESTAMP é naive — normaliza tudo pra naive UTC pra permitir comparação."""
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def ingest_event(raw_payload: dict) -> IngestResult:
    return _ingest_event(raw_payload, storage.get_connection())


def ingest_events(raw_payloads: list[dict]) -> tuple[IngestResult, ...]:
    """Ingest one listener batch atomically without changing event semantics.

    The listener remains the sole caller across the transaction-server boundary.
    A failure rolls back the whole batch and leaves its cursor untouched, so the
    same sequence can be retried safely through the existing event-id dedupe.
    """

    if not raw_payloads:
        return ()
    con = storage.get_connection()
    con.execute("BEGIN TRANSACTION")
    try:
        results = _ingest_batch(raw_payloads, con)
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    return tuple(results)


def _ingest_batch(raw_payloads: list[dict], con) -> list[IngestResult]:
    existing_ids = storage.existing_event_ids(
        con, [event_id for payload in raw_payloads if (event_id := payload.get("event_id"))]
    )
    accepted_ids: set[str] = set()
    candidates: list[tuple[int, str, dict, datetime, dict]] = []
    results: list[IngestResult | None] = [None] * len(raw_payloads)
    quarantined: list[tuple[str, datetime, dict, str]] = []

    for index, raw_payload in enumerate(raw_payloads):
        event_id = raw_payload.get("event_id") or ""
        received_at = datetime.now(timezone.utc).replace(tzinfo=None)
        if not event_id or event_id in existing_ids or event_id in accepted_ids:
            results[index] = IngestResult(status="DUPLICATE", event_id=event_id or "unknown", applied_to_current_state=False)
            continue

        canonical = normalize(raw_payload)
        errors = validate_canonical(canonical)
        if errors:
            reason = "; ".join(errors)
            quarantined.append((event_id, received_at, raw_payload, reason))
            results[index] = IngestResult(
                status="QUARANTINED", event_id=event_id, errors=errors, applied_to_current_state=False
            )
            continue

        accepted_ids.add(event_id)
        candidates.append((index, event_id, canonical, received_at, raw_payload))

    states = storage.current_attempt_states(con, [item[2]["attempt_id"] for item in candidates])
    raw_rows: list[tuple[str, datetime, dict]] = []
    canonical_rows: list[tuple[dict, datetime, bool, bool]] = []
    current_rows: dict[str, tuple[dict, datetime]] = {}
    for index, event_id, canonical, received_at, raw_payload in candidates:
        event_time = _parse_dt(canonical["event_time"])
        applied, is_late = _should_apply_state(states.get(canonical["attempt_id"]), event_time)
        if applied:
            states[canonical["attempt_id"]] = (canonical["status"], event_time)
            current_rows[canonical["attempt_id"]] = (canonical, event_time)
        raw_rows.append((event_id, received_at, raw_payload))
        canonical_rows.append((canonical, event_time, applied, is_late))
        results[index] = IngestResult(
            status="ACCEPTED", event_id=event_id, canonical=canonical, applied_to_current_state=applied
        )

    storage.store_raw_many(con, raw_rows)
    storage.store_canonical_events_many(con, canonical_rows)
    storage.upsert_current_states_many(con, list(current_rows.values()))
    storage.quarantine_many(con, quarantined)
    return [result for result in results if result is not None]


def _should_apply_state(current: tuple[str, datetime] | None, event_time: datetime) -> tuple[bool, bool]:
    if current is None:
        return True, False
    status, current_event_time = current
    if ordering.is_terminal(status):
        return False, False
    if event_time >= current_event_time:
        return True, False
    return False, (current_event_time - event_time) <= ordering.LATE_TOLERANCE


def _ingest_event(raw_payload: dict, con) -> IngestResult:
    event_id = raw_payload.get("event_id") or ""
    received_at = datetime.now(timezone.utc).replace(tzinfo=None)

    if not event_id or dedupe.is_duplicate(con, event_id):
        return IngestResult(status="DUPLICATE", event_id=event_id or "unknown", applied_to_current_state=False)

    canonical = normalize(raw_payload)
    errors = validate_canonical(canonical)
    if errors:
        dedupe.quarantine(con, event_id, received_at, raw_payload, "; ".join(errors))
        return IngestResult(status="QUARANTINED", event_id=event_id, errors=errors, applied_to_current_state=False)

    storage.store_raw(con, event_id, received_at, raw_payload)

    event_time = _parse_dt(canonical["event_time"])
    apply_update, is_late = ordering.should_apply(con, canonical["attempt_id"], event_time)
    storage.store_canonical_event(con, canonical, event_time, applied=apply_update, is_late=is_late)
    if apply_update:
        storage.upsert_current_state(con, canonical, event_time)

    return IngestResult(
        status="ACCEPTED", event_id=event_id, canonical=canonical, applied_to_current_state=apply_update
    )
