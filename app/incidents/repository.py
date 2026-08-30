"""DuckDB persistence for current Incidents.

Neo4j remains a repository of *historical* incidents for memory retrieval.  This
adapter stores the current, detector-produced Incident and its authorized
transaction links in the same durable store that owns the transaction lifecycle.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Mapping

from app.ingestion.storage import CONNECTION_LOCK, get_connection

from . import Incident


class IncidentIdConflictError(ValueError):
    """An incident ID was reused for a different causal fingerprint."""


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _as_utc_naive(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).replace(tzinfo=None)


def causal_fingerprint(incident: Incident | Mapping[str, Any]) -> str:
    """Fingerprint exactly one causal scope in one observed window.

    A shared country or correlation alone is intentionally insufficient: the
    complete scope and window are part of the key, so simultaneous causes remain
    independently queryable.
    """
    payload = incident.model_dump(mode="json") if isinstance(incident, Incident) else dict(incident)
    scope = payload.get("scope", {})
    if not isinstance(scope, Mapping) or not scope:
        raise ValueError("incident scope is required for a causal fingerprint")
    normalized_scope = {
        str(key): sorted(str(item) for item in value)
        for key, value in sorted(scope.items())
        if isinstance(value, list)
    }
    if not normalized_scope:
        raise ValueError("incident scope is required for a causal fingerprint")
    key = {
        "correlation_id": str(payload["correlation_id"]),
        "window_start": str(payload["estimated_started_at"]),
        "window_end": str(payload["detected_at"]),
        "scope": normalized_scope,
    }
    encoded = json.dumps(key, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


class DuckDBIncidentRepository:
    """Idempotent Incident store backed by the shared DuckDB connection."""

    def upsert(self, incident: Incident | Mapping[str, Any]) -> Incident:
        model = incident if isinstance(incident, Incident) else Incident.model_validate(incident)
        fingerprint = causal_fingerprint(model)
        now = _now()
        with CONNECTION_LOCK:
            con = get_connection()
            existing = con.execute(
                "SELECT incident_id, created_at FROM incident_records WHERE causal_fingerprint = ?", [fingerprint]
            ).fetchone()
            id_owner = con.execute(
                "SELECT causal_fingerprint FROM incident_records WHERE incident_id = ?", [model.incident_id]
            ).fetchone()
            if id_owner is not None and id_owner[0] != fingerprint:
                raise IncidentIdConflictError("incident_id is already bound to another causal fingerprint")
            if existing is not None:
                # Re-delivery is an update of the same causal Incident, never a new row.
                model = model.model_copy(update={"incident_id": existing[0]})
                created_at = existing[1]
            else:
                created_at = now
            payload_json = json.dumps(model.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
            con.execute(
                """INSERT INTO incident_records
                   (incident_id, causal_fingerprint, correlation_id, window_start, window_end, state, payload_json, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT (incident_id) DO UPDATE SET
                     causal_fingerprint = excluded.causal_fingerprint,
                     correlation_id = excluded.correlation_id,
                     window_start = excluded.window_start,
                     window_end = excluded.window_end,
                     state = excluded.state,
                     payload_json = excluded.payload_json,
                     updated_at = excluded.updated_at""",
                [
                    model.incident_id,
                    fingerprint,
                    model.correlation_id,
                    _as_utc_naive(model.estimated_started_at),
                    _as_utc_naive(model.detected_at),
                    model.state,
                    payload_json,
                    created_at,
                    now,
                ],
            )
        return model

    def get(self, incident_id: str) -> Incident | None:
        with CONNECTION_LOCK:
            row = get_connection().execute(
                "SELECT payload_json FROM incident_records WHERE incident_id = ?", [incident_id]
            ).fetchone()
        return Incident.model_validate_json(row[0]) if row else None

    def list(self, *, correlation_id: str | None = None) -> list[Incident]:
        where = "WHERE correlation_id = ?" if correlation_id is not None else ""
        values = [correlation_id] if correlation_id is not None else []
        with CONNECTION_LOCK:
            rows = get_connection().execute(
                f"SELECT payload_json FROM incident_records {where} ORDER BY window_end DESC, incident_id ASC", values
            ).fetchall()
        return [Incident.model_validate_json(row[0]) for row in rows]

    def link_transaction(
        self, transaction_id: str, incident_id: str, *, evidence_ids: list[str], correlation_id: str
    ) -> None:
        """Persist an explicit link only for matching correlation and evidence."""
        if not evidence_ids or any(not isinstance(item, str) or not item for item in evidence_ids):
            raise ValueError("transaction Incident links require at least one evidence ID")
        with CONNECTION_LOCK:
            con = get_connection()
            transaction = con.execute(
                "SELECT correlation_id FROM transaction_records WHERE transaction_id = ?", [transaction_id]
            ).fetchone()
            incident = con.execute(
                "SELECT correlation_id FROM incident_records WHERE incident_id = ?", [incident_id]
            ).fetchone()
            if transaction is None:
                raise KeyError("transaction not found")
            if incident is None:
                raise KeyError("incident not found")
            if transaction[0] != correlation_id or incident[0] != correlation_id:
                raise ValueError("transaction and Incident correlations must match")
            con.execute(
                """INSERT INTO transaction_incident_links
                   (transaction_id, incident_id, correlation_id, evidence_ids_json, linked_at)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT (transaction_id, incident_id) DO UPDATE SET
                     evidence_ids_json = excluded.evidence_ids_json,
                     linked_at = excluded.linked_at""",
                [transaction_id, incident_id, correlation_id, json.dumps(sorted(set(evidence_ids))), _now()],
            )

    def list_for_transaction(self, transaction_id: str) -> list[Incident]:
        with CONNECTION_LOCK:
            rows = get_connection().execute(
                """SELECT records.payload_json
                   FROM transaction_incident_links AS links
                   JOIN incident_records AS records USING (incident_id)
                   WHERE links.transaction_id = ? AND links.correlation_id = records.correlation_id
                   ORDER BY records.window_end DESC, records.incident_id ASC""",
                [transaction_id],
            ).fetchall()
        return [Incident.model_validate_json(row[0]) for row in rows]
