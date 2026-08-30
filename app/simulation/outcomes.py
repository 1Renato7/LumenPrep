"""TASK-DATA-002. Outcomes condicionais (via app.simulation.config, dimensão
`status`) + orquestração de retry, montando eventos no shape de CTR-EVT-001.

Fora de escopo aqui, deliberadamente (fica com TASK-DATA-004 do Renato):
- distribuição temporal com sazonalidade em 90 dias — todos os eventos saem
  perto de um único `reference_time`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import log
from random import Random
from typing import Any

from app.simulation.config import DeclineCode, GeneratorConfig
from app.simulation.sampling import DeterministicDimensionSampler

MAX_RETRIES = 2
RETRYABLE_STATUSES = {"DECLINED", "TIMEOUT"}
_RETRY_PROBABILITY = 0.6

_CURRENCY_BY_COUNTRY = {"BR": "BRL", "MX": "MXN", "CO": "COP"}

@dataclass(frozen=True)
class GeneratedAttempt:
    payment_id: str
    attempt_id: str
    attempt_sequence: int
    context: dict[str, str]
    status: str
    decline: DeclineCode | None = None


class OutcomeGenerator:
    """Amostra dimensao+status (app.simulation.config/sampling) e encadeia
    retries pra tentativas DECLINED/TIMEOUT retryable na mesma payment_id."""

    def __init__(self, config: GeneratorConfig, *, reference_time: datetime | None = None) -> None:
        self._config = config
        self._sampler = DeterministicDimensionSampler(config)
        self._random = Random(config.seed ^ 0x5A5A5A5A)
        self._reference_time = reference_time or datetime(2026, 8, 29, 14, 0, 0, tzinfo=timezone.utc)
        self._sequence = 0
        # Namespace pelo reference_time: cada instancia nova (ex.: um controller por
        # dia/sessao) precisa gerar IDs unicos mesmo sem estado compartilhado entre
        # instancias — sem isso, dois OutcomeGenerator com sequence=0 colidem em
        # event_id e o segundo vira DUPLICATE inteiro no dedupe (bug real achado
        # no smoke de integracao completo).
        self._id_namespace = int(self._reference_time.timestamp())

    def _next_id(self, prefix: str) -> str:
        self._sequence += 1
        return f"{prefix}_{self._id_namespace}_{self._sequence:06d}"

    def generate_payment(self) -> list[GeneratedAttempt]:
        payment_id = self._next_id("pay")
        attempts: list[GeneratedAttempt] = []
        for sequence in range(1, MAX_RETRIES + 2):
            context = self._sampler.sample_attempt()
            status = context["status"]
            attempt = GeneratedAttempt(
                payment_id=payment_id,
                attempt_id=self._next_id("att"),
                attempt_sequence=sequence,
                context=context,
                status=status,
                decline=self._sample_decline(context["provider_id"], status),
            )
            attempts.append(attempt)
            if attempt.status not in RETRYABLE_STATUSES:
                break
            if attempt.decline and attempt.decline.retryability == "DO_NOT_RETRY":
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
        timing = self._sample_timing(context["provider_id"], attempt.status)
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
            "timing": timing,
            "correlation_id": f"corr_{attempt.payment_id}",
            "is_test": True,
        }
        decline = attempt.decline or self._sample_decline(context["provider_id"], attempt.status)
        if decline is not None:
            canonical["decline"] = decline.as_payload()
        return canonical

    def _sample_decline(self, provider_id: str, status: str) -> DeclineCode | None:
        codes = self._config.decline_codes_for(provider_id, status)
        if not codes:
            return None
        threshold = self._random.random()
        cumulative = 0.0
        for code in codes:
            cumulative += code.probability
            if threshold < cumulative:
                return code
        return codes[-1]

    def _sample_timing(self, provider_id: str, status: str) -> dict[str, int]:
        profile = self._config.latency_profile_for(provider_id)
        # A log-normal distribution preserves a realistic positive right tail while
        # exposing the configured median and p95 for detector/eval calibration.
        sigma = log(profile.p95_ms / profile.p50_ms) / 1.6448536269514722
        provider_latency_ms = max(1, round(self._random.lognormvariate(log(profile.p50_ms), sigma)))
        if status in {"TIMEOUT", "ERROR"}:
            provider_latency_ms = round(provider_latency_ms * profile.timeout_multiplier)
        orchestrator_latency_ms = self._random.randint(profile.orchestrator_min_ms, profile.orchestrator_max_ms)
        return {
            "orchestrator_latency_ms": orchestrator_latency_ms,
            "provider_latency_ms": provider_latency_ms,
            "total_latency_ms": provider_latency_ms + orchestrator_latency_ms,
        }
