"""DuckDB persistence for agent suggestions, kept apart from the Incident row.

The suggestion is a separate record on purpose.  ``CTR-INC-001`` stays frozen,
readers who only want the engine's diagnosis are unaffected, and a suggestion
can be regenerated or dropped without rewriting the Incident.

Idempotency is keyed on incident + evidence fingerprint + model + prompt
version: reprocessing an unchanged Incident must not produce a second, subtly
different hypothesis.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256

from app.ingestion.storage import CONNECTION_LOCK, get_connection

from .models import DiagnosticSuggestion


def suggestion_idempotency_key(
    *, incident_id: str, evidence_fingerprint: str, model_version: str, prompt_version: str
) -> str:
    payload = json.dumps(
        {
            "incident_id": incident_id,
            "evidence_fingerprint": evidence_fingerprint,
            "model_version": model_version,
            "prompt_version": prompt_version,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class DiagnosticSuggestionRepository:
    """Append-or-refresh store for CTR-AGT-003 records."""

    def upsert(self, suggestion: DiagnosticSuggestion, *, idempotency_key: str, prompt_version: str) -> DiagnosticSuggestion:
        payload_json = json.dumps(suggestion.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        now = _now()
        suggestion_id = f"sug_{idempotency_key[:20]}"
        with CONNECTION_LOCK:
            con = get_connection()
            existing = con.execute(
                "SELECT created_at FROM incident_suggestions WHERE idempotency_key = ?", [idempotency_key]
            ).fetchone()
            created_at = existing[0] if existing is not None else now
            con.execute(
                """INSERT INTO incident_suggestions
                   (suggestion_id, incident_id, idempotency_key, evidence_fingerprint, model_version,
                    prompt_version, status, payload_json, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT (suggestion_id) DO UPDATE SET
                     incident_id = excluded.incident_id,
                     idempotency_key = excluded.idempotency_key,
                     evidence_fingerprint = excluded.evidence_fingerprint,
                     model_version = excluded.model_version,
                     prompt_version = excluded.prompt_version,
                     status = excluded.status,
                     payload_json = excluded.payload_json,
                     updated_at = excluded.updated_at""",
                [
                    suggestion_id,
                    suggestion.incident_id,
                    idempotency_key,
                    suggestion.evidence_fingerprint,
                    suggestion.model_version,
                    prompt_version,
                    suggestion.status,
                    payload_json,
                    created_at,
                    now,
                ],
            )
        return suggestion

    def get_by_idempotency_key(self, idempotency_key: str) -> DiagnosticSuggestion | None:
        with CONNECTION_LOCK:
            row = get_connection().execute(
                "SELECT payload_json FROM incident_suggestions WHERE idempotency_key = ?", [idempotency_key]
            ).fetchone()
        return DiagnosticSuggestion.model_validate_json(row[0]) if row else None

    def latest_for_incident(self, incident_id: str) -> DiagnosticSuggestion | None:
        """Return the most recent suggestion; a stale fingerprint never wins."""
        with CONNECTION_LOCK:
            row = get_connection().execute(
                """SELECT payload_json FROM incident_suggestions
                   WHERE incident_id = ?
                   ORDER BY updated_at DESC, suggestion_id ASC
                   LIMIT 1""",
                [incident_id],
            ).fetchone()
        return DiagnosticSuggestion.model_validate_json(row[0]) if row else None

    def count_for_incident(self, incident_id: str) -> int:
        with CONNECTION_LOCK:
            row = get_connection().execute(
                "SELECT count(*) FROM incident_suggestions WHERE incident_id = ?", [incident_id]
            ).fetchone()
        return int(row[0]) if row else 0
