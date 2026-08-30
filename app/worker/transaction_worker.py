"""TASK-TXN-WORKER-001 / CTR-TXL-001. Durable, restart-safe transaction lifecycle worker.

All state lives in ``transaction_records`` (app.ingestion.storage) — the worker keeps
nothing in process memory between calls. That is what makes a crash between stages, a
process restart or a duplicate delivery of the same transaction_id all resume/no-op
correctly instead of skipping or repeating work: whatever last got committed to the row
*is* the state, and every call re-reads it before acting.

``_generate_outcome`` is a deterministic placeholder seeded by transaction_id, standing
in for Renato's real TransactionInput -> outcome adapter (the actual blocker for this
task per docs/plans/people/rogerio.md). It can be swapped without touching the
persistence/lease/reconciliation logic below.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from random import Random
from typing import Any
from uuid import uuid4

from app.ingestion.storage import get_connection

STAGE_ORDER = ["RECEIVED", "NORMALIZING", "CLASSIFYING", "AGGREGATING", "ANALYZING", "COMPLETE"]
_PROGRESS_BY_STAGE = {stage: index * 20 for index, stage in enumerate(STAGE_ORDER)}
DEFAULT_LEASE_SECONDS = 30


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _generate_outcome(transaction_id: str) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Deterministic outcome+classification for ``transaction_id`` (placeholder, see module docstring).

    Same transaction_id always yields the same result, so re-running a stuck or
    re-delivered job never flips a prior decision.
    """
    seed = int.from_bytes(sha256(transaction_id.encode("utf-8")).digest()[:8], "big")
    rng = Random(seed)
    roll = rng.random()
    latency_ms = rng.randint(80, 2500)
    evidence_ids = [f"evd_{transaction_id}"]

    if roll < 0.72:
        outcome = {
            "result": "SUCCEEDED",
            "provider_response_code": "00",
            "normalized_decline_code": None,
            "latency_ms": latency_ms,
        }
        classification = {
            "category": "APPROVED",
            "reason": "Provider approved the attempt.",
            "confidence": round(rng.uniform(0.9, 0.99), 2),
            "evidence_ids": evidence_ids,
            "related_incident_ids": [],
        }
        return "SUCCEEDED", outcome, classification

    if roll < 0.94:
        category, reason, decline_code = rng.choice(
            [
                ("ISSUER_DECLINE", "Issuer declined the attempt.", "GENERIC_DECLINE"),
                ("PROVIDER_ERROR", "Provider returned an error response.", "PROVIDER_ERROR"),
                ("TIMEOUT", "Provider did not respond before timeout.", "TIMEOUT"),
            ]
        )
        outcome = {
            "result": "FAILED",
            "provider_response_code": "05",
            "normalized_decline_code": decline_code,
            "latency_ms": latency_ms,
        }
        classification = {
            "category": category,
            "reason": reason,
            "confidence": round(rng.uniform(0.6, 0.95), 2),
            "evidence_ids": evidence_ids,
            "related_incident_ids": [],
        }
        return "FAILED", outcome, classification

    outcome = {
        "result": "UNKNOWN",
        "provider_response_code": None,
        "normalized_decline_code": None,
        "latency_ms": latency_ms,
    }
    classification = {
        "category": "UNKNOWN",
        "reason": "Provider response was inconclusive.",
        "confidence": round(rng.uniform(0.3, 0.6), 2),
        "evidence_ids": evidence_ids,
        "related_incident_ids": [],
    }
    return "UNKNOWN", outcome, classification


def _acquire_lease(con, transaction_id: str, worker_id: str, lease_seconds: int) -> bool:
    """Atomically claim ``transaction_id`` if it is unleased or its lease expired.

    Two workers racing for the same stuck record: only the UPDATE that actually
    matches a row wins the lease, so the loser's ``RETURNING`` set is empty.
    """
    now = _now()
    expires_at = now + timedelta(seconds=lease_seconds)
    acquired = con.execute(
        """UPDATE transaction_records
           SET lease_owner = ?, lease_expires_at = ?
           WHERE transaction_id = ? AND status = 'PROCESSING'
             AND (lease_expires_at IS NULL OR lease_expires_at < ?)
           RETURNING transaction_id""",
        [worker_id, expires_at, transaction_id, now],
    ).fetchone()
    return acquired is not None


def _advance_locked(con, transaction_id: str) -> None:
    row = con.execute(
        "SELECT status, processing_json FROM transaction_records WHERE transaction_id = ?",
        [transaction_id],
    ).fetchone()
    if row is None or row[0] != "PROCESSING":
        return

    processing = json.loads(row[1])
    stage_index = STAGE_ORDER.index(processing["stage"])
    next_stage = STAGE_ORDER[stage_index + 1]
    now = _now()

    if next_stage != "COMPLETE":
        con.execute(
            """UPDATE transaction_records
               SET processing_json = ?, updated_at = ?, lease_owner = NULL, lease_expires_at = NULL
               WHERE transaction_id = ?""",
            [
                json.dumps({"stage": next_stage, "progress_percent": _PROGRESS_BY_STAGE[next_stage], "failure_code": None}),
                now,
                transaction_id,
            ],
        )
        return

    try:
        result, outcome, classification = _generate_outcome(transaction_id)
    except Exception as exc:  # a technical worker failure must never read as a business decline
        con.execute(
            """UPDATE transaction_records
               SET status = 'UNKNOWN', processing_json = ?, outcome_json = NULL, classification_json = NULL,
                   updated_at = ?, lease_owner = NULL, lease_expires_at = NULL
               WHERE transaction_id = ?""",
            [
                json.dumps({"stage": "PIPELINE_FAILED", "progress_percent": 100, "failure_code": f"WORKER_ERROR:{type(exc).__name__}"}),
                now,
                transaction_id,
            ],
        )
        return

    con.execute(
        """UPDATE transaction_records
           SET status = ?, processing_json = ?, outcome_json = ?, classification_json = ?,
               updated_at = ?, lease_owner = NULL, lease_expires_at = NULL
           WHERE transaction_id = ?""",
        [
            result,
            json.dumps({"stage": "COMPLETE", "progress_percent": 100, "failure_code": None}),
            json.dumps(outcome),
            json.dumps(classification),
            now,
            transaction_id,
        ],
    )


def advance_transaction(transaction_id: str, *, worker_id: str | None = None, lease_seconds: int = DEFAULT_LEASE_SECONDS) -> bool:
    """Advance ``transaction_id`` by exactly one stage. Returns False if it is not a
    leasable PROCESSING record (already terminal, or currently leased by someone else)."""
    con = get_connection()
    worker_id = worker_id or f"worker_{uuid4().hex[:8]}"
    if not _acquire_lease(con, transaction_id, worker_id, lease_seconds):
        return False
    _advance_locked(con, transaction_id)
    return True


def advance_one(*, worker_id: str | None = None, lease_seconds: int = DEFAULT_LEASE_SECONDS) -> str | None:
    """Pick the oldest leasable PROCESSING record in the whole table and advance it
    one stage. Returns its transaction_id, or None if nothing is leasable right now."""
    con = get_connection()
    now = _now()
    candidate = con.execute(
        """SELECT transaction_id FROM transaction_records
           WHERE status = 'PROCESSING' AND (lease_expires_at IS NULL OR lease_expires_at < ?)
           ORDER BY updated_at ASC LIMIT 1""",
        [now],
    ).fetchone()
    if candidate is None:
        return None
    transaction_id = candidate[0]
    if not advance_transaction(transaction_id, worker_id=worker_id, lease_seconds=lease_seconds):
        return None
    return transaction_id


def run_to_completion(transaction_id: str, *, worker_id: str | None = None) -> None:
    """Drive one transaction through every remaining stage. Safe to call again on an
    already-terminal or already-leased transaction — it becomes a no-op."""
    for _ in range(len(STAGE_ORDER)):
        con = get_connection()
        row = con.execute("SELECT status FROM transaction_records WHERE transaction_id = ?", [transaction_id]).fetchone()
        if row is None or row[0] != "PROCESSING":
            return
        if not advance_transaction(transaction_id, worker_id=worker_id):
            return


def run_batch_to_completion(batch_id: str) -> None:
    con = get_connection()
    ids = [r[0] for r in con.execute(
        "SELECT transaction_id FROM transaction_records WHERE batch_id = ?", [batch_id]
    ).fetchall()]
    for transaction_id in ids:
        run_to_completion(transaction_id)


def reconcile_stuck(*, max_records: int = 1000) -> int:
    """Resume every PROCESSING record found at startup (or on demand). Records with a
    live lease from a still-running worker are simply skipped by ``advance_transaction``'s
    lease check, so calling this concurrently with an active worker is harmless."""
    con = get_connection()
    ids = [r[0] for r in con.execute(
        "SELECT transaction_id FROM transaction_records WHERE status = 'PROCESSING' LIMIT ?", [max_records]
    ).fetchall()]
    for transaction_id in ids:
        run_to_completion(transaction_id)
    return len(ids)
