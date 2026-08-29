"""CMP-ING-001 — expõe ingest_event, IngestResult. Stub TASK-CORE-001; real impl TASK-ING-001..004."""

from typing import Literal

from pydantic import BaseModel


class IngestResult(BaseModel):
    status: Literal["ACCEPTED", "DUPLICATE", "QUARANTINED"]
    event_id: str
    canonical: dict | None = None
    errors: list[str] = []


def ingest_event(raw_payload: dict) -> IngestResult:
    """Stub. Real: TASK-ING-001..004, validate contra canonical-attempt.schema.json, dedupe, quarantine."""
    return IngestResult(
        status="ACCEPTED",
        event_id=raw_payload.get("event_id", "stub_event"),
        canonical=raw_payload,
    )
