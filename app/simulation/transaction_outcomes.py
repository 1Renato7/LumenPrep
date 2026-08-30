"""TASK-DATA-008 / LUM2-61 deterministic transaction outcome adapter.

The public transaction boundary supplies facts only. This module derives a terminal
outcome and canonical ``CTR-EVT-001`` event from those facts plus stable context; it
performs no I/O, so the worker can retry it safely.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from hashlib import sha256
import json
from math import log
from pathlib import Path
from random import Random
from typing import Any, Mapping

from app.simulation.config import DeclineCode, GeneratorConfig, WeightedValue, load_generator_config

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "generator" / "v1" / "default.json"
_EPOCH = datetime(2026, 8, 29, tzinfo=timezone.utc)
_EVENT_METHOD = {
    "CARD": "CARD",
    "BANK_TRANSFER": "REAL_TIME_PAYMENT",
    "DIGITAL_WALLET": "WALLET",
    "PIX": "REAL_TIME_PAYMENT",
    "SPEI": "REAL_TIME_PAYMENT",
    "PSE": "REAL_TIME_PAYMENT",
    "BOLETO": "CASH",
    "CASH_IN_STORE": "CASH",
    # CTR-EVT-001 has no generic OTHER value. Map it to a neutral rail while
    # retaining the honest UNKNOWN outcome below.
    "OTHER": "REAL_TIME_PAYMENT",
}


@dataclass(frozen=True)
class AdaptedTransaction:
    """Pure adapter output consumed by the durable transaction worker."""

    result: str
    outcome: dict[str, Any]
    classification: dict[str, Any]
    event: dict[str, Any]


def adapt_transaction(
    transaction: Mapping[str, Any],
    *,
    transaction_id: str,
    correlation_id: str,
    seed_context: str | None = None,
    config: GeneratorConfig | None = None,
) -> AdaptedTransaction:
    """Derive a deterministic outcome and canonical event without reading storage."""
    if not transaction_id or not correlation_id:
        raise ValueError("transaction_id and correlation_id are required")

    config = config or _default_config()
    payload = dict(transaction)
    rng = Random(_seed(payload, seed_context or transaction_id, config.fingerprint))
    status = _status_for(payload, rng, config)
    decline = _decline_for(payload, status, rng, config)
    timing = _timing_for(str(payload["provider_id"]), status, rng, config)
    result, classification = _classification_for(status, decline, transaction_id)
    outcome = {
        "result": result,
        "provider_response_code": "00" if result == "SUCCEEDED" else (decline.raw_code if decline else None),
        "normalized_decline_code": decline.normalized_code if decline else None,
        "latency_ms": timing["total_latency_ms"],
    }
    event_time = _event_time(payload.get("occurred_at"), rng)
    event = _event_for(
        payload,
        transaction_id=transaction_id,
        correlation_id=correlation_id,
        status=status,
        decline=decline,
        timing=timing,
        event_time=event_time,
    )
    return AdaptedTransaction(result=result, outcome=outcome, classification=classification, event=event)


def _seed(transaction: Mapping[str, Any], seed_context: str, config_fingerprint: str) -> int:
    material = json.dumps(transaction, sort_keys=True, separators=(",", ":"), default=str)
    digest = sha256(f"{config_fingerprint}:{seed_context}:{material}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


@lru_cache
def _default_config() -> GeneratorConfig:
    """Load the immutable versioned generator profile once per worker process."""
    return load_generator_config(_CONFIG_PATH)


def _status_for(transaction: Mapping[str, Any], rng: Random, config: GeneratorConfig) -> str:
    if transaction["payment_method_category"] == "OTHER":
        return "UNKNOWN"
    context = {
        "country": str(transaction["country"]),
        "merchant_id": str(transaction["merchant_id"]),
        "provider_id": str(transaction["provider_id"]),
        "payment_method_category": str(transaction["payment_method_category"]),
    }
    return _weighted_choice(config.distribution_for("status", context), rng)


def _weighted_choice(values: tuple[WeightedValue, ...], rng: Random) -> str:
    threshold = rng.random()
    cumulative = 0.0
    for value in values:
        cumulative += value.probability
        if threshold < cumulative:
            return value.identifier
    return values[-1].identifier


def _decline_for(
    transaction: Mapping[str, Any], status: str, rng: Random, config: GeneratorConfig
) -> DeclineCode | None:
    if status not in {"DECLINED", "TIMEOUT", "ERROR"}:
        return None
    return _weighted_decline(config.decline_codes_for(str(transaction["provider_id"]), status), rng)


def _weighted_decline(codes: tuple[DeclineCode, ...], rng: Random) -> DeclineCode:
    threshold = rng.random()
    cumulative = 0.0
    for code in codes:
        cumulative += code.probability
        if threshold < cumulative:
            return code
    return codes[-1]


def _timing_for(provider_id: str, status: str, rng: Random, config: GeneratorConfig) -> dict[str, int]:
    profile = config.latency_profile_for(provider_id)
    sigma = log(profile.p95_ms / profile.p50_ms) / 1.6448536269514722
    provider_latency_ms = max(1, round(rng.lognormvariate(log(profile.p50_ms), sigma)))
    if status in {"TIMEOUT", "ERROR"}:
        provider_latency_ms = round(provider_latency_ms * profile.timeout_multiplier)
    orchestrator_latency_ms = rng.randint(profile.orchestrator_min_ms, profile.orchestrator_max_ms)
    return {
        "orchestrator_latency_ms": orchestrator_latency_ms,
        "provider_latency_ms": provider_latency_ms,
        "total_latency_ms": provider_latency_ms + orchestrator_latency_ms,
    }


def _classification_for(status: str, decline: DeclineCode | None, transaction_id: str) -> tuple[str, dict[str, Any]]:
    evidence_ids = [f"evd_{transaction_id}"]
    if status == "SUCCEEDED":
        return "SUCCEEDED", {
            "category": "APPROVED",
            "reason": "Synthetic provider approved the attempt.",
            "confidence": 0.95,
            "evidence_ids": evidence_ids,
            "related_incident_ids": [],
        }
    if status == "UNKNOWN":
        return "UNKNOWN", {
            "category": "UNKNOWN",
            "reason": "Synthetic provider outcome is unavailable for this payment rail.",
            "confidence": 0.35,
            "evidence_ids": evidence_ids,
            "related_incident_ids": [],
        }
    category = "TIMEOUT" if status == "TIMEOUT" else "ISSUER_DECLINE"
    if status == "ERROR" or (decline and decline.category in {"PROVIDER", "TECHNICAL"}):
        category = "PROVIDER_ERROR"
    return "FAILED", {
        "category": category,
        "reason": f"Synthetic {status.lower()} outcome from the configured provider profile.",
        "confidence": 0.85,
        "evidence_ids": evidence_ids,
        "related_incident_ids": [],
    }


def _event_time(occurred_at: Any, rng: Random) -> datetime:
    if occurred_at:
        if isinstance(occurred_at, datetime):
            value = occurred_at
        else:
            value = datetime.fromisoformat(str(occurred_at).replace("Z", "+00:00"))
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    return _EPOCH + timedelta(seconds=rng.randrange(0, 86_400))


def _event_for(
    transaction: Mapping[str, Any],
    *,
    transaction_id: str,
    correlation_id: str,
    status: str,
    decline: DeclineCode | None,
    timing: dict[str, int],
    event_time: datetime,
) -> dict[str, Any]:
    timestamp = event_time.isoformat().replace("+00:00", "Z")
    is_card = transaction["payment_method_category"] == "CARD"
    card_type = transaction.get("card_type")
    if card_type == "NOT_APPLICABLE":
        card_type = "UNKNOWN"
    return {
        "schema_version": "1.0",
        "event_id": f"evt_{transaction_id}",
        "event_type": "PAYMENT_ATTEMPT_CREATED",
        "event_time": timestamp,
        "received_at": timestamp,
        "payment_id": f"pay_{transaction_id}",
        "attempt_id": f"att_{transaction_id}",
        "attempt_sequence": 1,
        "merchant_id": transaction["merchant_id"],
        "provider_id": transaction["provider_id"],
        "provider_connection_id": transaction.get("provider_connection_id"),
        "country": transaction["country"],
        "currency": transaction["currency"],
        "amount_minor": transaction["amount_minor"],
        "payment_method_category": _EVENT_METHOD[transaction["payment_method_category"]],
        "payment_method_type": card_type if is_card else None,
        "card": {
            "brand": transaction.get("card_brand"),
            "type": card_type,
            "issuer_bank_id": transaction["issuer_bank"],
            "issuer_country": transaction["country"],
            "bin_prefix": None,
        } if is_card else None,
        "status": status,
        "decline": decline.as_payload() if decline else None,
        "timing": timing,
        "raw_event_id": None,
        "normalization_version": "1.0",
        "correlation_id": correlation_id,
        "is_test": True,
    }
