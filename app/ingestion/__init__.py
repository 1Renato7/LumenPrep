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
    event_id = raw_payload.get("event_id") or ""
    con = storage.get_connection()
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
