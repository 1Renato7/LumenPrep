"""TASK-ING-001. Único módulo que fala DuckDB para raw/canonical.

raw_events: imutável, append-only, nunca update.
canonical_events: versionado — uma linha por evento canônico válido (revision = ordem de chegada).
canonical_attempts: estado atual por attempt_id, só atualizado quando ordering.should_apply libera.
"""

import json
from datetime import datetime

import duckdb

from app.config import settings

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
    correlation_id VARCHAR NOT NULL
);
"""

_connection: duckdb.DuckDBPyConnection | None = None


def get_connection() -> duckdb.DuckDBPyConnection:
    global _connection
    if _connection is None:
        _connection = duckdb.connect(settings.duckdb_path)
        _connection.execute(_SCHEMA_SQL)
    return _connection


def reset_connection() -> None:
    """Só para testes — força reabertura (fixture in-memory por teste)."""
    global _connection
    _connection = None


def store_raw(con, event_id: str, received_at: datetime, raw_payload: dict) -> None:
    con.execute(
        "INSERT INTO raw_events (event_id, received_at, raw_json) VALUES (?, ?, ?)",
        [event_id, received_at, json.dumps(raw_payload)],
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
