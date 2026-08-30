"""CTR-TXN-001 / CTR-TXL-001 public transaction-first API.

Only synthetic transaction facts cross this boundary.  Outcome, classification and
progress are authored by the worker; newly accepted records deliberately remain in
``PROCESSING`` until that worker advances them.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from random import Random, SystemRandom
from typing import Annotated, Any, Literal
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

from app.ingestion.storage import CONNECTION_LOCK, get_connection
from app.worker.transaction_worker import run_batch_to_completion

router = APIRouter(prefix="/v1", tags=["transactions"])

MAX_BATCH_SIZE = 100
_SYSTEM_RANDOM = SystemRandom()
_CATALOG = {
    "merchants": ("merchant_br_01", "merchant_mx_01"),
    "providers": ("provider_alpha", "provider_beta"),
    "issuer_banks": ("bank_br_a", "bank_br_b", "bank_br_c", "bank_mx_a"),
    "countries": ("BR", "MX"),
    "currencies": ("BRL", "MXN"),
    "payment_method_categories": ("CARD", "DIGITAL_WALLET", "BANK_TRANSFER"),
    "card_brands": ("MASTERCARD", "VISA"),
    "card_types": ("CREDIT", "DEBIT", "PREPAID", "NOT_APPLICABLE"),
}
_ISSUERS_BY_COUNTRY = {
    "BR": ("bank_br_a", "bank_br_b", "bank_br_c"),
    "MX": ("bank_mx_a",),
}
_CURRENCY_BY_COUNTRY = {"BR": "BRL", "MX": "MXN"}


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TransactionInput(_StrictModel):
    client_reference: str | None = Field(default=None, min_length=1, max_length=100)
    occurred_at: datetime | None = None
    merchant_id: str = Field(min_length=1, max_length=100)
    provider_id: str = Field(min_length=1, max_length=100)
    issuer_bank: str = Field(min_length=1, max_length=100)
    country: Annotated[str, Field(pattern=r"^[A-Z]{2}$")]
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    amount_minor: int = Field(ge=1)
    payment_method_category: Literal["CARD", "BANK_TRANSFER", "DIGITAL_WALLET", "OTHER"]
    card_brand: str | None = Field(default=None, max_length=50)
    card_type: Literal["CREDIT", "DEBIT", "PREPAID", "NOT_APPLICABLE"] | None = None
    provider_connection_id: str | None = Field(default=None, max_length=100)
    channel: Literal["WEB", "MOBILE", "POS", "API"] | None = None


class SampleDefaults(_StrictModel):
    merchant_id: str | None = None
    country: Annotated[str | None, Field(pattern=r"^[A-Z]{2}$")] = None
    currency: Annotated[str | None, Field(pattern=r"^[A-Z]{3}$")] = None


class SampleRequest(_StrictModel):
    schema_version: Literal["1.0"]
    count: int = Field(ge=1, le=MAX_BATCH_SIZE)
    seed: int | None = Field(default=None, ge=0)
    defaults: SampleDefaults | None = None


class BatchRequest(_StrictModel):
    schema_version: Literal["1.0"]
    idempotency_key: str = Field(min_length=8, max_length=100)
    transactions: list[TransactionInput] = Field(min_length=1, max_length=MAX_BATCH_SIZE)


class IdempotencyConflict(Exception):
    """An existing idempotency key was submitted with a different payload."""


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _iso(value: datetime) -> str:
    return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _correlation_id() -> str:
    return f"corr_{uuid4().hex}"


def _catalog_response() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "max_batch_size": MAX_BATCH_SIZE,
        **{key: list(value) for key, value in _CATALOG.items()},
        "correlation_id": _correlation_id(),
    }


def _validate_sample_defaults(defaults: SampleDefaults | None) -> SampleDefaults:
    defaults = defaults or SampleDefaults()
    if defaults.merchant_id and defaults.merchant_id not in _CATALOG["merchants"]:
        raise HTTPException(status_code=422, detail="INVALID_SAMPLE_DEFAULT")
    if defaults.country and defaults.country not in _CATALOG["countries"]:
        raise HTTPException(status_code=422, detail="INVALID_SAMPLE_DEFAULT")
    if defaults.currency and defaults.currency not in _CATALOG["currencies"]:
        raise HTTPException(status_code=422, detail="INVALID_SAMPLE_DEFAULT")
    if defaults.country and defaults.currency and _CURRENCY_BY_COUNTRY[defaults.country] != defaults.currency:
        raise HTTPException(status_code=422, detail="INVALID_SAMPLE_DEFAULT")
    return defaults


def _sample_transactions(request: SampleRequest) -> tuple[int, list[dict[str, Any]]]:
    defaults = _validate_sample_defaults(request.defaults)
    seed = request.seed if request.seed is not None else _SYSTEM_RANDOM.randrange(0, 2**31)
    random = Random(seed)
    transactions: list[dict[str, Any]] = []
    for index in range(request.count):
        country = defaults.country or random.choice(_CATALOG["countries"])
        currency = defaults.currency or _CURRENCY_BY_COUNTRY[country]
        method = random.choice(_CATALOG["payment_method_categories"])
        is_card = method == "CARD"
        transactions.append(
            {
                "client_reference": f"sample-{seed}-{index + 1}",
                "occurred_at": None,
                "merchant_id": defaults.merchant_id or random.choice(_CATALOG["merchants"]),
                "provider_id": random.choice(_CATALOG["providers"]),
                "issuer_bank": random.choice(_ISSUERS_BY_COUNTRY[country]),
                "country": country,
                "currency": currency,
                "amount_minor": random.choice((1990, 7990, 12990, 21990, 25990)),
                "payment_method_category": method,
                "card_brand": random.choice(_CATALOG["card_brands"]) if is_card else None,
                "card_type": random.choice(("CREDIT", "DEBIT", "PREPAID")) if is_card else "NOT_APPLICABLE",
                "provider_connection_id": f"conn_{country.lower()}_primary",
                "channel": random.choice(("WEB", "MOBILE")),
            }
        )
    return seed, transactions


def _fingerprint(request: BatchRequest) -> str:
    payload = request.model_dump(mode="json")
    payload.pop("idempotency_key")
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def _record_from_row(row: tuple[Any, ...]) -> dict[str, Any]:
    (
        transaction_id,
        batch_id,
        created_at,
        updated_at,
        state,
        input_json,
        processing_json,
        outcome_json,
        classification_json,
        correlation_id,
    ) = row
    return {
        "schema_version": "1.0",
        "transaction_id": transaction_id,
        "batch_id": batch_id,
        "created_at": _iso(created_at),
        "updated_at": _iso(updated_at),
        "status": state,
        "input": json.loads(input_json),
        "processing": json.loads(processing_json),
        "outcome": json.loads(outcome_json) if outcome_json else None,
        "classification": json.loads(classification_json) if classification_json else None,
        "correlation_id": correlation_id,
    }


_RECORD_COLUMNS = """
transaction_id, batch_id, created_at, updated_at, status, input_json,
processing_json, outcome_json, classification_json, correlation_id
"""


def _batch_response(batch_id: str) -> dict[str, Any]:
    con = get_connection()
    batch = con.execute(
        "SELECT accepted_at, correlation_id FROM transaction_batches WHERE batch_id = ?", [batch_id]
    ).fetchone()
    if batch is None:
        raise KeyError(batch_id)
    ids = [row[0] for row in con.execute(
        "SELECT transaction_id FROM transaction_records WHERE batch_id = ? ORDER BY batch_position", [batch_id]
    ).fetchall()]
    return {
        "schema_version": "1.0",
        "batch_id": batch_id,
        "accepted_at": _iso(batch[0]),
        "status": "PROCESSING",
        "transaction_ids": ids,
        "correlation_id": batch[1],
    }


def _create_batch(request: BatchRequest) -> dict[str, Any]:
    with CONNECTION_LOCK:
        con = get_connection()
        fingerprint = _fingerprint(request)
        existing = con.execute(
            "SELECT batch_id, payload_fingerprint FROM transaction_batches WHERE idempotency_key = ?",
            [request.idempotency_key],
        ).fetchone()
        if existing:
            if existing[1] != fingerprint:
                raise IdempotencyConflict()
            return _batch_response(existing[0])

        batch_id = f"batch_{uuid4().hex}"
        accepted_at = _now()
        correlation_id = _correlation_id()
        try:
            con.execute("BEGIN TRANSACTION")
            con.execute(
                """INSERT INTO transaction_batches
                   (batch_id, idempotency_key, payload_fingerprint, accepted_at, correlation_id)
                   VALUES (?, ?, ?, ?, ?)""",
                [batch_id, request.idempotency_key, fingerprint, accepted_at, correlation_id],
            )
            for position, item in enumerate(request.transactions):
                transaction_id = f"txn_{uuid4().hex}"
                con.execute(
                    """INSERT INTO transaction_records
                       (transaction_id, batch_id, batch_position, created_at, updated_at, status,
                        input_json, processing_json, outcome_json, classification_json, correlation_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?)""",
                    [
                        transaction_id,
                        batch_id,
                        position,
                        accepted_at,
                        accepted_at,
                        "PROCESSING",
                        json.dumps(item.model_dump(mode="json"), sort_keys=True),
                        json.dumps({"stage": "RECEIVED", "progress_percent": 0, "failure_code": None}),
                        correlation_id,
                    ],
                )
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
        return _batch_response(batch_id)


def _list_records(*, batch_id: str | None = None, state: str | None = None, cursor: str | None = None, limit: int = 50) -> dict[str, Any]:
    try:
        offset = int(cursor) if cursor else 0
    except ValueError as error:
        raise HTTPException(status_code=422, detail="INVALID_CURSOR") from error
    if offset < 0:
        raise HTTPException(status_code=422, detail="INVALID_CURSOR")
    clauses: list[str] = []
    values: list[Any] = []
    if batch_id is not None:
        clauses.append("batch_id = ?")
        values.append(batch_id)
    if state is not None:
        clauses.append("status = ?")
        values.append(state)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with CONNECTION_LOCK:
        rows = get_connection().execute(
            f"SELECT {_RECORD_COLUMNS} FROM transaction_records {where} "
            "ORDER BY created_at DESC, transaction_id DESC LIMIT ? OFFSET ?",
            [*values, limit + 1, offset],
        ).fetchall()
    has_next = len(rows) > limit
    records = [_record_from_row(row) for row in rows[:limit]]
    return {
        "schema_version": "1.0",
        "items": records,
        "next_cursor": str(offset + limit) if has_next else None,
        "correlation_id": _correlation_id(),
    }


@router.get("/transaction-catalog")
def get_transaction_catalog() -> dict[str, Any]:
    return _catalog_response()


@router.post("/transaction-samples")
def generate_transaction_samples(request: SampleRequest) -> dict[str, Any]:
    seed, transactions = _sample_transactions(request)
    return {"schema_version": "1.0", "seed": seed, "transactions": transactions, "correlation_id": _correlation_id()}


@router.post("/transaction-batches", status_code=status.HTTP_202_ACCEPTED)
def create_transaction_batch(
    request: BatchRequest,
    background_tasks: BackgroundTasks,
    idempotency_header: Annotated[str, Header(alias="Idempotency-Key", min_length=8)],
) -> dict[str, Any]:
    if idempotency_header != request.idempotency_key:
        raise HTTPException(status_code=422, detail="IDEMPOTENCY_KEY_REQUIRED_OR_MISMATCH")
    try:
        response = _create_batch(request)
    except IdempotencyConflict as error:
        raise HTTPException(status_code=409, detail="IDEMPOTENCY_KEY_CONFLICT") from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="INGESTION_UNAVAILABLE") from error
    background_tasks.add_task(run_batch_to_completion, response["batch_id"])
    return response


@router.get("/transaction-batches/{batch_id}")
def get_transaction_batch(batch_id: str) -> dict[str, Any]:
    result = _list_records(batch_id=batch_id, limit=MAX_BATCH_SIZE)
    if not result["items"]:
        # A batch is always inserted atomically with 1..100 records, so an empty
        # result means the batch itself never existed — no separate lookup needed.
        raise HTTPException(status_code=404, detail="BATCH_NOT_FOUND")
    return result


@router.get("/transactions")
def list_transactions(
    status_filter: Annotated[Literal["PROCESSING", "SUCCEEDED", "FAILED", "UNKNOWN"] | None, Query(alias="status")] = None,
    cursor: str | None = None,
    limit: int = Query(default=50, ge=1, le=MAX_BATCH_SIZE),
) -> dict[str, Any]:
    return _list_records(state=status_filter, cursor=cursor, limit=limit)


@router.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: str) -> dict[str, Any]:
    with CONNECTION_LOCK:
        row = get_connection().execute(
            f"SELECT {_RECORD_COLUMNS} FROM transaction_records WHERE transaction_id = ?", [transaction_id]
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="TRANSACTION_NOT_FOUND")
    return _record_from_row(row)
