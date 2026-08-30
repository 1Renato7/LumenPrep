"""TASK-TXN-WORKER-001 / CTR-TXL-001. Durable, restart-safe transaction lifecycle worker.

All state lives in ``transaction_records`` (app.ingestion.storage) — the worker keeps
nothing in process memory between calls. That is what makes a crash between stages, a
process restart or a duplicate delivery of the same transaction_id all resume/no-op
correctly instead of skipping or repeating work: whatever last got committed to the row
*is* the state, and every call re-reads it before acting.

``_generate_outcome`` delegates to Renato's deterministic TransactionInput adapter;
the worker remains responsible only for durable lifecycle and event persistence.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from app.ingestion import ingest_event
from app.ingestion.storage import CONNECTION_LOCK, get_connection
from app.refusal_codes import RefusalCodeLookup, resolve_refusal_code
from app.simulation.transaction_outcomes import AdaptedTransaction, adapt_transaction
from app.worker.incident_pipeline import SuggestionJob, _suggest_for_persisted_incident, derive_incidents_for_correlation

STAGE_ORDER = ["RECEIVED", "NORMALIZING", "CLASSIFYING", "AGGREGATING", "ANALYZING", "COMPLETE"]
_PROGRESS_BY_STAGE = {stage: index * 20 for index, stage in enumerate(STAGE_ORDER)}
DEFAULT_LEASE_SECONDS = 30


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _generate_outcome(
    transaction_id: str, transaction_input: dict[str, Any], correlation_id: str
) -> AdaptedTransaction:
    """Adapt a persisted input and, when present, apply its versioned response-code fact."""
    adapted = adapt_transaction(
        transaction_input,
        transaction_id=transaction_id,
        correlation_id=correlation_id,
    )
    response_code = transaction_input.get("provider_response_code")
    if not response_code:
        return adapted
    resolution = resolve_refusal_code(
        get_connection(),
        RefusalCodeLookup(
            str(transaction_input["provider_id"]),
            str(transaction_input["issuer_bank"]),
            str(transaction_input.get("card_brand") or "NOT_APPLICABLE"),
            str(response_code),
        ),
    )
    payload = resolution.as_payload()
    result = resolution.outcome
    classification = dict(adapted.classification)
    classification.update({
        "category": "APPROVED" if result == "SUCCEEDED" else ("ISSUER_DECLINE" if result == "FAILED" else "UNKNOWN"),
        "reason": resolution.reason or "No unique mapping was found for this provider response code.",
        "confidence": 1.0 if resolution.lookup_status.value == "MATCH_FOUND" else 0.35,
        "refusal_resolution": payload,
    })
    outcome = dict(adapted.outcome)
    outcome.update({"result": result, "provider_response_code": resolution.response_code,
                    "normalized_decline_code": (f"RESPONSE_CODE_{resolution.response_code}" if result == "FAILED" else None)})
    event = dict(adapted.event)
    event["status"] = {"SUCCEEDED": "SUCCEEDED", "FAILED": "DECLINED", "UNKNOWN": "ERROR"}[result]
    event["decline"] = None if result == "SUCCEEDED" else {
        "normalized_code": outcome["normalized_decline_code"] or "UNMAPPED_DECLINE",
        "category": "ISSUER", "retryability": "UNKNOWN", "raw_code": resolution.response_code,
        "raw_message": resolution.reason or "Unmapped provider response code",
    }
    return AdaptedTransaction(result=result, outcome=outcome, classification=classification, event=event)


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


def _advance_locked(con, transaction_id: str) -> list[SuggestionJob]:
    row = con.execute(
        "SELECT status, processing_json, input_json, correlation_id FROM transaction_records WHERE transaction_id = ?",
        [transaction_id],
    ).fetchone()
    if row is None or row[0] != "PROCESSING":
        return []

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
        return []

    transaction_started = False
    suggestion_jobs: list[SuggestionJob] = []
    try:
        adapted = _generate_outcome(transaction_id, json.loads(row[2]), row[3])
        con.execute("BEGIN TRANSACTION")
        transaction_started = True
        # Make the current transaction eligible for evidence-authorized linking.
        # API readers use the same CONNECTION_LOCK, so they cannot observe this
        # provisional PROCESSING + classification state.
        con.execute(
            "UPDATE transaction_records SET classification_json = ? WHERE transaction_id = ?",
            [json.dumps(adapted.classification), transaction_id],
        )
        ingestion = ingest_event(adapted.event)
        if ingestion.status not in {"ACCEPTED", "DUPLICATE"}:
            raise RuntimeError(f"canonical event was {ingestion.status}")
        derive_incidents_for_correlation(con, row[3], suggestion_jobs=suggestion_jobs)
        authored_classification = con.execute(
            "SELECT classification_json FROM transaction_records WHERE transaction_id = ?",
            [transaction_id],
        ).fetchone()[0]
        con.execute(
            """UPDATE transaction_records
               SET status = ?, processing_json = ?, outcome_json = ?, classification_json = ?,
                   updated_at = ?, lease_owner = NULL, lease_expires_at = NULL
               WHERE transaction_id = ?""",
            [
                adapted.result,
                json.dumps({"stage": "COMPLETE", "progress_percent": 100, "failure_code": None}),
                json.dumps(adapted.outcome),
                authored_classification,
                now,
                transaction_id,
            ],
        )
        con.execute("COMMIT")
        transaction_started = False
    except Exception as exc:  # a technical worker failure must never read as a business decline
        if transaction_started:
            con.execute("ROLLBACK")
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
        return []
    return suggestion_jobs


def advance_transaction(transaction_id: str, *, worker_id: str | None = None, lease_seconds: int = DEFAULT_LEASE_SECONDS) -> bool:
    """Advance ``transaction_id`` by exactly one stage. Returns False if it is not a
    leasable PROCESSING record (already terminal, or currently leased by someone else).

    Holds CONNECTION_LOCK for the whole lease-acquire-then-advance sequence — the
    shared DuckDB connection is not safe for concurrent use across threads, and
    ``create_transaction_batch``'s background task means this genuinely runs from
    several threadpool threads at once.
    """
    con = get_connection()
    worker_id = worker_id or f"worker_{uuid4().hex[:8]}"
    with CONNECTION_LOCK:
        if not _acquire_lease(con, transaction_id, worker_id, lease_seconds):
            return False
        suggestion_jobs = _advance_locked(con, transaction_id)
    for job in suggestion_jobs:
        # Keep older in-process worker tests/jobs compatible while every newly
        # created job carries the RFC summary as its third value.
        incident, decline_profile = job[0], job[1]
        refusal_code_summaries = job[2] if len(job) > 2 else []
        _suggest_for_persisted_incident(incident, decline_profile, refusal_code_summaries)
    return True


def advance_one(*, worker_id: str | None = None, lease_seconds: int = DEFAULT_LEASE_SECONDS) -> str | None:
    """Pick the oldest leasable PROCESSING record in the whole table and advance it
    one stage. Returns its transaction_id, or None if nothing is leasable right now."""
    con = get_connection()
    now = _now()
    with CONNECTION_LOCK:
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
        with CONNECTION_LOCK:
            row = get_connection().execute(
                "SELECT status FROM transaction_records WHERE transaction_id = ?", [transaction_id]
            ).fetchone()
        if row is None or row[0] != "PROCESSING":
            return
        if not advance_transaction(transaction_id, worker_id=worker_id):
            return


def run_batch_to_completion(batch_id: str) -> None:
    with CONNECTION_LOCK:
        ids = [r[0] for r in get_connection().execute(
            "SELECT transaction_id FROM transaction_records WHERE batch_id = ?", [batch_id]
        ).fetchall()]
    for transaction_id in ids:
        run_to_completion(transaction_id)


def reconcile_stuck(*, max_records: int = 1000) -> int:
    """Resume every PROCESSING record found at startup (or on demand). Records with a
    live lease from a still-running worker are simply skipped by ``advance_transaction``'s
    lease check, so calling this concurrently with an active worker is harmless."""
    with CONNECTION_LOCK:
        ids = [r[0] for r in get_connection().execute(
            "SELECT transaction_id FROM transaction_records WHERE status = 'PROCESSING' LIMIT ?", [max_records]
        ).fetchall()]
    for transaction_id in ids:
        run_to_completion(transaction_id)
    return len(ids)
