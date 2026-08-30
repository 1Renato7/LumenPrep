"""TASK-DATA-009 / LUM2-62: background traffic submitted through the public batch API.

Reuses the deterministic dimension generator from ``renato/tarefa44``
(``GeneratorConfig`` + ``DeterministicDimensionSampler``) but deliberately does not
preserve its local transport (``TransactionServer``/``IngestionListenerWorker``): every
fact generated here is submitted through the same ``POST /v1/transaction-batches`` path
a real client would use, so metrics only move once the worker processes the batch. See
``docs/flight-log.md`` FL-20260829-TEAM-018 (DEC-017) for why the transport was not
carried over while the generator was.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from random import Random, SystemRandom
from typing import Any
from uuid import uuid4

from app.api.transactions import MAX_BATCH_SIZE, BatchRequest, TransactionInput, _create_batch
from app.simulation.config import GeneratorConfig, load_generator_config
from app.simulation.sampling import DeterministicDimensionSampler
from app.worker.transaction_worker import run_batch_to_completion

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "generator" / "v1" / "default.json"
_SYSTEM_RANDOM = SystemRandom()

_CURRENCY_BY_COUNTRY = {"BR": "BRL", "MX": "MXN", "CO": "COP"}
_ISSUER_BANKS_BY_COUNTRY = {
    "BR": ("bank_br_a", "bank_br_b", "bank_br_c"),
    "MX": ("bank_mx_a",),
    "CO": ("bank_co_a", "bank_co_b"),
}
_CARD_BRANDS = ("MASTERCARD", "VISA")
_CARD_TYPES = ("CREDIT", "DEBIT", "PREPAID")
_CHANNELS = ("WEB", "MOBILE", "POS", "API")
_AMOUNTS_MINOR = (1990, 4990, 7990, 12990, 21990, 25990)
_METHOD_MAP = {"WALLET": "DIGITAL_WALLET"}


def _load_config(seed: int) -> GeneratorConfig:
    base = load_generator_config(_CONFIG_PATH)
    return replace(base, seed=seed)


def _to_transaction_input(sample: dict[str, str], *, index: int, seed: int, rng: Random) -> dict[str, Any]:
    country = sample["country"]
    provider_id = sample["provider_id"]
    method = _METHOD_MAP.get(sample["payment_method_category"], sample["payment_method_category"])
    is_card = method == "CARD"
    return {
        "client_reference": f"bgtraffic-{seed}-{index + 1}",
        "occurred_at": None,
        "merchant_id": sample["merchant_id"],
        "provider_id": provider_id,
        "issuer_bank": rng.choice(_ISSUER_BANKS_BY_COUNTRY[country]),
        "country": country,
        "currency": _CURRENCY_BY_COUNTRY[country],
        "amount_minor": rng.choice(_AMOUNTS_MINOR),
        "payment_method_category": method,
        "card_brand": rng.choice(_CARD_BRANDS) if is_card else None,
        "card_type": rng.choice(_CARD_TYPES) if is_card else "NOT_APPLICABLE",
        "provider_connection_id": f"conn_{country.lower()}_{provider_id}",
        "channel": rng.choice(_CHANNELS),
    }


def generate_background_transactions(count: int, *, seed: int | None = None) -> tuple[int, list[dict[str, Any]]]:
    """Deterministically sample ``count`` transaction facts (no outcome/status)."""
    if not 1 <= count <= MAX_BATCH_SIZE:
        raise ValueError(f"count must be between 1 and {MAX_BATCH_SIZE}")
    seed = seed if seed is not None else _SYSTEM_RANDOM.randrange(0, 2**31)
    sampler = DeterministicDimensionSampler(_load_config(seed))
    rng = Random(seed)
    samples = sampler.sample_attempts(count)
    transactions = [
        _to_transaction_input(sample, index=index, seed=seed, rng=rng) for index, sample in enumerate(samples)
    ]
    return seed, transactions


def submit_background_batch(count: int, *, seed: int | None = None) -> dict[str, Any]:
    """Generate background traffic and submit it through the same batch API a real
    client uses. This harness never writes to DuckDB directly."""
    seed, transactions = generate_background_transactions(count, seed=seed)
    request = BatchRequest(
        schema_version="1.0",
        idempotency_key=f"bgtraffic_{uuid4().hex}",
        transactions=[TransactionInput(**item) for item in transactions],
    )
    response = _create_batch(request)
    run_batch_to_completion(response["batch_id"])
    return {**response, "seed": seed}
