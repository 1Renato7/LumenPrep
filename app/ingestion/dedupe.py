"""TASK-ING-003. Idempotency key (event_id) + quarantine de inválidos."""

import json
from datetime import datetime


def is_duplicate(con, event_id: str) -> bool:
    row = con.execute("SELECT 1 FROM raw_events WHERE event_id = ?", [event_id]).fetchone()
    return row is not None


def quarantine(con, event_id: str, received_at: datetime, raw_payload: dict, reason: str) -> None:
    con.execute(
        "INSERT INTO quarantine (event_id, received_at, reason, raw_json) VALUES (?, ?, ?, ?)",
        [event_id, received_at, reason, json.dumps(raw_payload)],
    )
