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


class ReviewIdConflictError(ValueError):
    """A review id was reused for a different human decision."""


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


def recurrence_key(incident: Incident | Mapping[str, Any]) -> str | None:
    """Identify the operational type of an Incident across distinct windows.

    Delivery identity intentionally includes correlation and time window. A
    recurrence must not: it is the same supported causal category, metric and
    complete operational scope observed again later. An inconclusive Incident
    has no named causal type and is therefore kept as its own first occurrence.
    """
    payload = incident.model_dump(mode="json") if isinstance(incident, Incident) else dict(incident)
    root_cause = payload.get("root_cause", {})
    category = root_cause.get("category") if isinstance(root_cause, Mapping) else None
    if not isinstance(category, str) or not category:
        return None
    scope = payload.get("scope", {})
    if not isinstance(scope, Mapping) or not scope:
        raise ValueError("incident scope is required for a recurrence key")
    normalized_scope = {
        str(key): sorted(str(item) for item in value)
        for key, value in sorted(scope.items())
        if isinstance(value, list)
    }
    if not normalized_scope:
        raise ValueError("incident scope is required for a recurrence key")
    metrics = payload.get("metrics", {})
    metric = metrics.get("metric") if isinstance(metrics, Mapping) else None
    encoded = json.dumps(
        {"category": category, "metric": str(metric or "UNSPECIFIED"), "scope": normalized_scope},
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(encoded.encode("utf-8")).hexdigest()


def _utc_string(value: datetime) -> str:
    return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class DuckDBIncidentRepository:
    """Idempotent Incident store backed by the shared DuckDB connection."""

    def upsert(self, incident: Incident | Mapping[str, Any]) -> Incident:
        return self.upsert_with_status(incident)[0]

    def upsert_with_status(self, incident: Incident | Mapping[str, Any]) -> tuple[Incident, bool]:
        """Upsert one Incident and report whether this delivery created it.

        The boolean is deliberately derived from the causal fingerprint inside
        the same database transaction. Consumers can create side effects (the
        in-app notification) without treating replay as a new Incident.
        """
        model = incident if isinstance(incident, Incident) else Incident.model_validate(incident)
        fingerprint = causal_fingerprint(model)
        now = _now()
        with CONNECTION_LOCK:
            con = get_connection()
            _backfill_recurrence_metadata(con)
            key = recurrence_key(model)
            detected_at = _as_utc_naive(model.detected_at)
            first_detected_at = detected_at
            if key is not None:
                previous = con.execute(
                    """SELECT MIN(COALESCE(recurrence_first_detected_at, window_end))
                       FROM incident_records WHERE recurrence_key = ?""",
                    [key],
                ).fetchone()
                if previous is not None and previous[0] is not None:
                    first_detected_at = min(detected_at, previous[0])
            model = model.model_copy(update={"recurrence_first_detected_at": _utc_string(first_detected_at)})
            existing = con.execute(
                "SELECT incident_id, created_at FROM incident_records WHERE causal_fingerprint = ?", [fingerprint]
            ).fetchone()
            id_owner = con.execute(
                "SELECT causal_fingerprint FROM incident_records WHERE incident_id = ?", [model.incident_id]
            ).fetchone()
            if id_owner is not None and id_owner[0] != fingerprint:
                raise IncidentIdConflictError("incident_id is already bound to another causal fingerprint")
            created = existing is None
            if existing is not None:
                # Re-delivery is an update of the same causal Incident, never a new row.
                model = model.model_copy(update={"incident_id": existing[0]})
                created_at = existing[1]
            else:
                created_at = now
            payload_json = json.dumps(model.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
            con.execute(
                """INSERT INTO incident_records
                   (incident_id, causal_fingerprint, correlation_id, window_start, window_end, recurrence_key, recurrence_first_detected_at, state, payload_json, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT (incident_id) DO UPDATE SET
                     causal_fingerprint = excluded.causal_fingerprint,
                     correlation_id = excluded.correlation_id,
                     window_start = excluded.window_start,
                     window_end = excluded.window_end,
                     recurrence_key = excluded.recurrence_key,
                     recurrence_first_detected_at = excluded.recurrence_first_detected_at,
                     state = excluded.state,
                     payload_json = excluded.payload_json,
                     updated_at = excluded.updated_at""",
                [
                    model.incident_id,
                    fingerprint,
                    model.correlation_id,
                    _as_utc_naive(model.estimated_started_at),
                    _as_utc_naive(model.detected_at),
                    key,
                    first_detected_at,
                    model.state,
                    payload_json,
                    created_at,
                    now,
                ],
            )
        return model, created

    def create_notification(self, incident_id: str) -> None:
        """Persist exactly one unread notification for an Incident."""
        with CONNECTION_LOCK:
            con = get_connection()
            now = _now()
            digest = sha256(f"notification:{incident_id}".encode("utf-8")).hexdigest()[:20]
            con.execute(
                """INSERT INTO incident_notifications (notification_id, incident_id, created_at, read_at)
                   VALUES (?, ?, ?, NULL) ON CONFLICT (incident_id) DO NOTHING""",
                [f"ntf_{digest}", incident_id, now],
            )

    def notifications(self) -> list[dict[str, Any]]:
        with CONNECTION_LOCK:
            rows = get_connection().execute(
                """SELECT notification_id, incident_id, created_at, read_at
                   FROM incident_notifications ORDER BY created_at DESC, notification_id ASC"""
            ).fetchall()
        return [{"notification_id": row[0], "incident_id": row[1], "created_at": row[2].replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
                 "read_at": row[3].replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z") if row[3] else None}
                for row in rows]

    def mark_notification_read(self, notification_id: str) -> bool:
        with CONNECTION_LOCK:
            row = get_connection().execute(
                """UPDATE incident_notifications SET read_at = COALESCE(read_at, ?)
                   WHERE notification_id = ? RETURNING notification_id""", [_now(), notification_id]
            ).fetchone()
        return row is not None

    def get(self, incident_id: str) -> Incident | None:
        with CONNECTION_LOCK:
            con = get_connection()
            _backfill_recurrence_metadata(con)
            row = con.execute(
                "SELECT payload_json, recurrence_first_detected_at FROM incident_records WHERE incident_id = ?", [incident_id]
            ).fetchone()
        return _incident_from_row(row) if row else None

    def list(self, *, correlation_id: str | None = None) -> list[Incident]:
        where = "WHERE correlation_id = ?" if correlation_id is not None else ""
        values = [correlation_id] if correlation_id is not None else []
        with CONNECTION_LOCK:
            con = get_connection()
            _backfill_recurrence_metadata(con)
            rows = con.execute(
                f"SELECT payload_json, recurrence_first_detected_at FROM incident_records {where} ORDER BY window_end DESC, incident_id ASC", values
            ).fetchall()
        return [_incident_from_row(row) for row in rows]

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
            con = get_connection()
            _backfill_recurrence_metadata(con)
            rows = con.execute(
                """SELECT records.payload_json, records.recurrence_first_detected_at
                   FROM transaction_incident_links AS links
                   JOIN incident_records AS records USING (incident_id)
                   WHERE links.transaction_id = ? AND links.correlation_id = records.correlation_id
                   ORDER BY records.window_end DESC, records.incident_id ASC""",
                [transaction_id],
            ).fetchall()
        return [_incident_from_row(row) for row in rows]

    def record_review(
        self, *, review_id: str, incident_id: str, decision: str, reviewer_id: str,
        reason: str, confirmed_cause: str | None = None, playbook_id: str | None = None,
    ) -> dict[str, Any]:
        """Durably record one human decision before mirroring it to the graph.

        Retrying the exact submission is safe. Reusing its identifier with a
        different decision is rejected rather than silently changing an audit
        record or a historical precedent.
        """
        value = (review_id, incident_id, decision, reviewer_id, reason, confirmed_cause, playbook_id)
        with CONNECTION_LOCK:
            con = get_connection()
            if con.execute("SELECT 1 FROM incident_records WHERE incident_id = ?", [incident_id]).fetchone() is None:
                raise KeyError("incident not found")
            existing = con.execute(
                """SELECT incident_id, decision, reviewer_id, reason, confirmed_cause, playbook_id, reviewed_at
                   FROM incident_reviews WHERE review_id = ?""", [review_id]
            ).fetchone()
            if existing is not None:
                previous = existing[:6]
                if previous != value[1:]:
                    raise ReviewIdConflictError("review_id is already bound to another human decision")
                return _review_row(review_id, existing)
            reviewed_at = _now()
            con.execute(
                """INSERT INTO incident_reviews
                   (review_id, incident_id, decision, reviewer_id, reason, confirmed_cause, playbook_id, reviewed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [*value, reviewed_at],
            )
        return {
            "review_id": review_id, "incident_id": incident_id, "decision": decision,
            "reviewer_id": reviewer_id, "reason": reason, "confirmed_cause": confirmed_cause,
            "playbook_id": playbook_id, "reviewed_at": reviewed_at.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        }


def _review_row(review_id: str, row: tuple[Any, ...]) -> dict[str, Any]:
    return {
        "review_id": review_id, "incident_id": row[0], "decision": row[1], "reviewer_id": row[2],
        "reason": row[3], "confirmed_cause": row[4], "playbook_id": row[5],
        "reviewed_at": row[6].replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _incident_from_row(row: tuple[Any, ...]) -> Incident:
    model = Incident.model_validate_json(row[0])
    first_detected_at = row[1]
    if model.recurrence_first_detected_at is not None or first_detected_at is None:
        return model
    return model.model_copy(update={"recurrence_first_detected_at": _utc_string(first_detected_at)})


def _backfill_recurrence_metadata(con: Any) -> None:
    """Upgrade existing incident and transaction JSON without changing their IDs.

    Railway volumes can contain records from before recurrence metadata existed.
    The current store is small in the hackathon runtime, so a deterministic
    backfill at repository access is safer than requiring an external migration
    command and immediately makes legacy rows visible in the log.
    """
    rows = con.execute(
        """SELECT incident_id, payload_json, window_end, recurrence_key,
                  recurrence_first_detected_at FROM incident_records"""
    ).fetchall()
    if not rows:
        return
    parsed: list[tuple[str, Incident, datetime, str | None, datetime | None]] = []
    earliest: dict[str, datetime] = {}
    for incident_id, payload_json, window_end, stored_key, stored_first in rows:
        model = Incident.model_validate_json(payload_json)
        key = recurrence_key(model)
        detected_at = _as_utc_naive(model.detected_at)
        if key is not None:
            earliest[key] = min(earliest.get(key, detected_at), detected_at)
        parsed.append((incident_id, model, window_end, key, stored_first))

    recurrence_dates: dict[str, str] = {}
    for incident_id, model, window_end, key, stored_first in parsed:
        first = earliest[key] if key is not None else _as_utc_naive(model.detected_at)
        first_value = _utc_string(first)
        recurrence_dates[incident_id] = first_value
        if stored_key == key and stored_first == first and model.recurrence_first_detected_at == first_value:
            continue
        updated = model.model_copy(update={"recurrence_first_detected_at": first_value})
        con.execute(
            """UPDATE incident_records
               SET recurrence_key = ?, recurrence_first_detected_at = ?, payload_json = ?
               WHERE incident_id = ?""",
            [key, first, json.dumps(updated.model_dump(mode="json"), sort_keys=True, separators=(",", ":")), incident_id],
        )

    transaction_rows = con.execute(
        "SELECT transaction_id, classification_json FROM transaction_records WHERE classification_json IS NOT NULL"
    ).fetchall()
    for transaction_id, classification_json in transaction_rows:
        try:
            classification = json.loads(classification_json)
        except (TypeError, json.JSONDecodeError):
            continue
        related_ids = classification.get("related_incident_ids", [])
        if not isinstance(related_ids, list):
            continue
        related_incidents = [
            {"incident_id": incident_id, "recurrence_first_detected_at": recurrence_dates.get(incident_id)}
            for incident_id in sorted({str(item) for item in related_ids if isinstance(item, str) and item})
        ]
        if classification.get("related_incidents") == related_incidents:
            continue
        classification["related_incidents"] = related_incidents
        con.execute(
            "UPDATE transaction_records SET classification_json = ? WHERE transaction_id = ?",
            [json.dumps(classification, sort_keys=True), transaction_id],
        )
