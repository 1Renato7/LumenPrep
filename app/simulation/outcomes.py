"""TASK-DATA-002. Outcomes condicionais (via app.simulation.config, dimensão
`status`) + orquestração de retry, montando eventos no shape de CTR-EVT-001.

Fora de escopo aqui, deliberadamente (ficam com TASK-DATA-003/004 do Renato):
- decline codes/categorias realistas — usa um placeholder genérico;
- latência "coerente" por provider/percentil — usa um placeholder simples;
- distribuição temporal com sazonalidade em 90 dias — todos os eventos saem
  perto de um único `reference_time`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from random import Random
from typing import Any

from app.simulation.config import GeneratorConfig
from app.simulation.sampling import DeterministicDimensionSampler

MAX_RETRIES = 2
RETRYABLE_STATUSES = {"DECLINED", "TIMEOUT"}
_RETRY_PROBABILITY = 0.6

_CURRENCY_BY_COUNTRY = {"BR": "BRL", "MX": "MXN", "CO": "COP"}

_DECLINE_PLACEHOLDER: dict[str, Any] = {
    "normalized_code": "GENERIC_DECLINE",
    "category": "PROVIDER",
    "retryability": "RETRY_LATER",
    "raw_code": None,
    "raw_message": None,
    "mapping_version": "placeholder-pending-TASK-DATA-003",
}


@dataclass(frozen=True)
class GeneratedAttempt:
    payment_id: str
    attempt_id: str
    attempt_sequence: int
    context: dict[str, str]
    status: str


class OutcomeGenerator:
    """Amostra dimensao+status (app.simulation.config/sampling) e encadeia
    retries pra tentativas DECLINED/TIMEOUT retryable na mesma payment_id."""

    def __init__(self, config: GeneratorConfig, *, reference_time: datetime | None = None) -> None:
        self._sampler = DeterministicDimensionSampler(config)
        self._random = Random(config.seed ^ 0x5A5A5A5A)
        self._reference_time = reference_time or datetime(2026, 8, 29, 14, 0, 0, tzinfo=timezone.utc)
        self._sequence = 0

    def _next_id(self, prefix: str) -> str:
        self._sequence += 1
        return f"{prefix}_{self._sequence:09d}"

    def generate_payment(self) -> list[GeneratedAttempt]:
        payment_id = self._next_id("pay")
        attempts: list[GeneratedAttempt] = []
        for sequence in range(1, MAX_RETRIES + 2):
            context = self._sampler.sample_attempt()
            attempt = GeneratedAttempt(
                payment_id=payment_id,
                attempt_id=self._next_id("att"),
                attempt_sequence=sequence,
                context=context,
                status=context["status"],
            )
            attempts.append(attempt)
            if attempt.status not in RETRYABLE_STATUSES:
                break
            if self._random.random() >= _RETRY_PROBABILITY:
                break
        return attempts

    def generate_payments(self, count: int) -> list[list[GeneratedAttempt]]:
        if count < 0:
            raise ValueError("count must be non-negative")
        return [self.generate_payment() for _ in range(count)]

    def to_canonical_events(self, attempts: list[GeneratedAttempt]) -> list[dict[str, Any]]:
        events = []
        for offset, attempt in enumerate(attempts):
            event_time = self._reference_time + timedelta(seconds=offset * 2)
            events.append(self._to_canonical(attempt, event_time))
        return events

    def _sample_amount_minor(self) -> int:
        return self._random.randint(1_000, 500_000)

    def _to_canonical(self, attempt: GeneratedAttempt, event_time: datetime) -> dict[str, Any]:
        context = attempt.context
        country = context["country"]
        currency = _CURRENCY_BY_COUNTRY.get(country, "USD")
        event_time_iso = event_time.isoformat().replace("+00:00", "Z")
        is_slow = attempt.status in {"TIMEOUT", "ERROR"}
        provider_latency_ms = self._random.randint(2500, 6000) if is_slow else self._random.randint(150, 1800)
        canonical: dict[str, Any] = {
            "schema_version": "1.0",
            "event_id": self._next_id("evt"),
            "event_type": "PAYMENT_ATTEMPT_CREATED" if attempt.attempt_sequence == 1 else "PAYMENT_ATTEMPT_UPDATED",
            "event_time": event_time_iso,
            "received_at": event_time_iso,
            "payment_id": attempt.payment_id,
            "attempt_id": attempt.attempt_id,
            "attempt_sequence": attempt.attempt_sequence,
            "merchant_id": context["merchant_id"],
            "provider_id": context["provider_id"],
            "country": country,
            "currency": currency,
            "amount_minor": self._sample_amount_minor(),
            "payment_method_category": context["payment_method_category"],
            "status": attempt.status,
            "timing": {
                "provider_latency_ms": provider_latency_ms,
                "total_latency_ms": provider_latency_ms + self._random.randint(10, 80),
            },
            "correlation_id": f"corr_{attempt.payment_id}",
            "is_test": True,
        }
        if attempt.status == "DECLINED":
            canonical["decline"] = dict(_DECLINE_PLACEHOLDER)
        return canonical
