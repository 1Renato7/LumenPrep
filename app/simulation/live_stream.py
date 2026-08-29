"""TASK-DATA-006. Stream ao vivo (trafego normal continuo, TASK-DATA-002) +
injecao de cenarios (CTR-SCN-001), aplicando `effects` sobre as tentativas
que casam `filters`, e ingerindo de verdade via app.ingestion.ingest_event.

decline_code_distribution do CTR-SCN-001 nao e aplicado ainda — decline
codes realistas sao TASK-DATA-003 (Renato); aqui so approval_rate_multiplier,
latency_p95_multiplier e timeout_rate.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from random import Random
from typing import Any

from app.ingestion import IngestResult, ingest_event
from app.simulation.config import GeneratorConfig
from app.simulation.outcomes import GeneratedAttempt, OutcomeGenerator
from app.simulation.scenario_contract import ScenarioDefinition


@dataclass(frozen=True)
class InjectionResult:
    scenario_id: str
    correlation_id: str
    events_ingested: int
    matched_attempts: int
    accepted: int
    quarantined: int


def _matches_filters(context: dict[str, str], filters: dict[str, tuple[str, ...]]) -> bool:
    if not filters:
        return True
    return all(context.get(dimension) in values for dimension, values in filters.items())


def _resample_status(random_gen: Random, base_status: str, effects: dict[str, Any]) -> str:
    timeout_rate = effects.get("timeout_rate")
    if timeout_rate is not None and random_gen.random() < timeout_rate:
        return "TIMEOUT"
    multiplier = effects.get("approval_rate_multiplier")
    if multiplier is None:
        return base_status
    roll = random_gen.random()
    if base_status == "SUCCEEDED" and multiplier < 1.0:
        if roll < (1.0 - multiplier):
            return "DECLINED"
    elif base_status != "SUCCEEDED" and multiplier > 1.0:
        if roll < min(multiplier - 1.0, 1.0):
            return "SUCCEEDED"
    return base_status


def _apply_latency_effect(event: dict[str, Any], multiplier: float | None) -> dict[str, Any]:
    if multiplier is None:
        return event
    timing = dict(event["timing"])
    timing["provider_latency_ms"] = round(timing["provider_latency_ms"] * multiplier)
    timing["total_latency_ms"] = round(timing["total_latency_ms"] * multiplier)
    event = dict(event)
    event["timing"] = timing
    return event


class LiveStreamController:
    """Trafego normal continuo + injecao de cenario sobre o mesmo gerador seedado."""

    def __init__(self, config: GeneratorConfig, *, reference_time: datetime | None = None) -> None:
        self._config = config
        self._generator = OutcomeGenerator(config, reference_time=reference_time)
        self._random = Random(config.seed ^ 0xC0FFEE)

    def emit_baseline_batch(self, payment_count: int) -> list[IngestResult]:
        """Trafego normal, sem nenhum efeito de cenario — D1 do roteiro de demo."""
        results: list[IngestResult] = []
        for attempts in self._generator.generate_payments(payment_count):
            for event in self._generator.to_canonical_events(attempts):
                results.append(ingest_event(event))
        return results

    def inject_scenario(self, scenario: ScenarioDefinition, *, payment_count: int = 50) -> InjectionResult:
        """Gera `payment_count` payments; nas tentativas que casam `scenario.filters`,
        reamostra o status e escala a latencia pelos `effects` de CTR-SCN-001;
        ingere tudo (matched e nao-matched) de verdade via ingest_event."""
        matched = 0
        results: list[IngestResult] = []
        latency_multiplier = scenario.effects.get("latency_p95_multiplier")

        for attempts in self._generator.generate_payments(payment_count):
            adjusted: list[GeneratedAttempt] = []
            matched_flags: list[bool] = []
            for attempt in attempts:
                is_match = _matches_filters(attempt.context, scenario.filters)
                matched_flags.append(is_match)
                if is_match:
                    matched += 1
                    attempt = replace(attempt, status=_resample_status(self._random, attempt.status, scenario.effects))
                adjusted.append(attempt)

            for attempt, event, is_match in zip(adjusted, self._generator.to_canonical_events(adjusted), matched_flags):
                if is_match:
                    event = _apply_latency_effect(event, latency_multiplier)
                    event["correlation_id"] = f"demo:{scenario.scenario_id}"
                results.append(ingest_event(event))

        return InjectionResult(
            scenario_id=scenario.scenario_id,
            correlation_id=f"demo:{scenario.scenario_id}",
            events_ingested=len(results),
            matched_attempts=matched,
            accepted=sum(1 for r in results if r.status == "ACCEPTED"),
            quarantined=sum(1 for r in results if r.status == "QUARANTINED"),
        )
