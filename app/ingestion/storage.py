"""TASK-ING-001. Único módulo que fala DuckDB para raw/canonical.

raw_events: imutável, append-only, nunca update.
canonical_events: versionado — uma linha por evento canônico válido (revision = ordem de chegada).
canonical_attempts: estado atual por attempt_id, só atualizado quando ordering.should_apply libera.
"""

import json
from datetime import datetime
from threading import Lock

import duckdb

from app.config import settings

# The single shared DuckDB connection below is not safe for concurrent use from
# multiple threads (FastAPI runs sync `def` handlers, and background tasks, in a
# threadpool). Every caller that executes a query against get_connection() from
# request/background-task code must hold this lock for the duration of that access —
# see app.api.transactions._create_batch and app.worker.transaction_worker for the
# pattern. Reproduced directly without it: concurrent access corrupts query parameter
# binding across threads and DuckDB raises TransactionException / ConversionException.
CONNECTION_LOCK = Lock()

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS raw_events (
    event_id VARCHAR PRIMARY KEY,
    received_at TIMESTAMP,
    raw_json VARCHAR
);
CREATE TABLE IF NOT EXISTS canonical_events (
    event_id VARCHAR PRIMARY KEY,
    attempt_id VARCHAR,
    payment_id VARCHAR,
    event_time TIMESTAMP,
    status VARCHAR,
    is_late BOOLEAN,
    applied BOOLEAN,
    canonical_json VARCHAR
);
CREATE TABLE IF NOT EXISTS canonical_attempts (
    attempt_id VARCHAR PRIMARY KEY,
    payment_id VARCHAR,
    latest_event_id VARCHAR,
    event_time TIMESTAMP,
    status VARCHAR,
    canonical_json VARCHAR
);
CREATE TABLE IF NOT EXISTS quarantine (
    event_id VARCHAR,
    received_at TIMESTAMP,
    reason VARCHAR,
    raw_json VARCHAR
);
CREATE TABLE IF NOT EXISTS transaction_batches (
    batch_id VARCHAR PRIMARY KEY,
    idempotency_key VARCHAR UNIQUE NOT NULL,
    payload_fingerprint VARCHAR NOT NULL,
    accepted_at TIMESTAMP NOT NULL,
    correlation_id VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS transaction_records (
    transaction_id VARCHAR PRIMARY KEY,
    batch_id VARCHAR NOT NULL,
    batch_position INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    status VARCHAR NOT NULL,
    input_json VARCHAR NOT NULL,
    processing_json VARCHAR NOT NULL,
    outcome_json VARCHAR,
    classification_json VARCHAR,
    correlation_id VARCHAR NOT NULL,
    lease_owner VARCHAR,
    lease_expires_at TIMESTAMP
);
"""

_MIGRATION_SQL = """
ALTER TABLE transaction_records ADD COLUMN IF NOT EXISTS lease_owner VARCHAR;
ALTER TABLE transaction_records ADD COLUMN IF NOT EXISTS lease_expires_at TIMESTAMP;
"""

_connection: duckdb.DuckDBPyConnection | None = None


def get_connection() -> duckdb.DuckDBPyConnection:
    global _connection
    if _connection is None:
        _connection = duckdb.connect(settings.duckdb_path)
        _connection.execute(_SCHEMA_SQL)
        # Existing Railway Volumes can predate the durable-worker lease columns.
        # Upgrade them in place before the startup reconciliation reads those fields.
        _connection.execute(_MIGRATION_SQL)
    return _connection


def reset_connection() -> None:
    """Só para testes — força reabertura (fixture in-memory por teste)."""
    global _connection
    _connection = None


def related_incident_ids_for_transaction(transaction_id: str) -> list[str] | None:
    """Return the contract-authored incident links for one transaction.

    ``None`` means the transaction is unknown; an empty list is a known transaction
    with no related Incident.  Keeping this query in the storage adapter prevents
    the incident API from inventing a second view of transaction persistence.
    """
    with CONNECTION_LOCK:
        row = get_connection().execute(
            "SELECT classification_json FROM transaction_records WHERE transaction_id = ?",
            [transaction_id],
        ).fetchone()
    if row is None:
        return None
    if not row[0]:
        return []
    try:
        related_ids = json.loads(row[0]).get("related_incident_ids", [])
    except (TypeError, json.JSONDecodeError):
        return []
    return [incident_id for incident_id in related_ids if isinstance(incident_id, str) and incident_id]


def transaction_record_for_grounding(transaction_id: str) -> dict[str, object] | None:
    """Read only the persisted fields required by the grounded trace resolver.

    The incidents API must not recreate a second transaction view or infer a
    link from scope.  Returning the authored correlation and classification lets
    the explanation layer enforce its evidence/correlation guardrail.
    """
    with CONNECTION_LOCK:
        row = get_connection().execute(
            """SELECT transaction_id, correlation_id, classification_json
               FROM transaction_records WHERE transaction_id = ?""",
            [transaction_id],
        ).fetchone()
    if row is None:
        return None
    classification: object = None
    if row[2]:
        try:
            classification = json.loads(row[2])
        except (TypeError, json.JSONDecodeError):
            classification = None
    return {
        "transaction_id": row[0],
        "correlation_id": row[1],
        "classification": classification,
    }


def store_raw(con, event_id: str, received_at: datetime, raw_payload: dict) -> None:
    con.execute(
        "INSERT INTO raw_events (event_id, received_at, raw_json) VALUES (?, ?, ?)",
        [event_id, received_at, json.dumps(raw_payload)],
    )


def existing_event_ids(con, event_ids: list[str]) -> set[str]:
    if not event_ids:
        return set()
    placeholders = ", ".join("?" for _ in event_ids)
    return {row[0] for row in con.execute(f"SELECT event_id FROM raw_events WHERE event_id IN ({placeholders})", event_ids).fetchall()}


def current_attempt_states(con, attempt_ids: list[str]) -> dict[str, tuple[str, datetime]]:
    if not attempt_ids:
        return {}
    placeholders = ", ".join("?" for _ in attempt_ids)
    return {
        attempt_id: (status, event_time)
        for attempt_id, status, event_time in con.execute(
            f"SELECT attempt_id, status, event_time FROM canonical_attempts WHERE attempt_id IN ({placeholders})",
            attempt_ids,
        ).fetchall()
    }


def store_raw_many(con, rows: list[tuple[str, datetime, dict]]) -> None:
    if not rows:
        return
    con.executemany(
        "INSERT INTO raw_events (event_id, received_at, raw_json) VALUES (?, ?, ?)",
        [(event_id, received_at, json.dumps(raw_payload)) for event_id, received_at, raw_payload in rows],
    )


def store_canonical_event(
    con, canonical: dict, event_time: datetime, applied: bool, is_late: bool
) -> None:
    con.execute(
        """INSERT INTO canonical_events
           (event_id, attempt_id, payment_id, event_time, status, is_late, applied, canonical_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            canonical["event_id"],
            canonical["attempt_id"],
            canonical["payment_id"],
            event_time,
            canonical["status"],
            is_late,
            applied,
            json.dumps(canonical),
        ],
    )


def store_canonical_events_many(con, rows: list[tuple[dict, datetime, bool, bool]]) -> None:
    if not rows:
        return
    con.executemany(
        """INSERT INTO canonical_events
           (event_id, attempt_id, payment_id, event_time, status, is_late, applied, canonical_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                canonical["event_id"],
                canonical["attempt_id"],
                canonical["payment_id"],
                event_time,
                canonical["status"],
                is_late,
                applied,
                json.dumps(canonical),
            )
            for canonical, event_time, applied, is_late in rows
        ],
    )


def upsert_current_state(con, canonical: dict, event_time: datetime) -> None:
    con.execute(
        """INSERT INTO canonical_attempts
               (attempt_id, payment_id, latest_event_id, event_time, status, canonical_json)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT (attempt_id) DO UPDATE SET
               latest_event_id = excluded.latest_event_id,
               event_time = excluded.event_time,
               status = excluded.status,
               canonical_json = excluded.canonical_json""",
        [
            canonical["attempt_id"],
            canonical["payment_id"],
            canonical["event_id"],
            event_time,
            canonical["status"],
            json.dumps(canonical),
        ],
    )


def upsert_current_states_many(con, rows: list[tuple[dict, datetime]]) -> None:
    if not rows:
        return
    con.executemany(
        """INSERT INTO canonical_attempts
               (attempt_id, payment_id, latest_event_id, event_time, status, canonical_json)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT (attempt_id) DO UPDATE SET
               latest_event_id = excluded.latest_event_id,
               event_time = excluded.event_time,
               status = excluded.status,
               canonical_json = excluded.canonical_json""",
        [
            (
                canonical["attempt_id"],
                canonical["payment_id"],
                canonical["event_id"],
                event_time,
                canonical["status"],
                json.dumps(canonical),
            )
            for canonical, event_time in rows
        ],
    )


def quarantine_many(con, rows: list[tuple[str, datetime, dict, str]]) -> None:
    if not rows:
        return
    con.executemany(
        "INSERT INTO quarantine (event_id, received_at, reason, raw_json) VALUES (?, ?, ?, ?)",
        [(event_id, received_at, reason, json.dumps(raw_payload)) for event_id, received_at, raw_payload, reason in rows],
    )
