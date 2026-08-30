"""TASK-DATA-006. Stream ao vivo (trafego normal continuo, TASK-DATA-002) +
injecao de cenarios (CTR-SCN-001), aplicando `effects` sobre as tentativas
que casam `filters`, e publicando-as em CTR-STR-001.

`decline_code_distribution` do CTR-SCN-001 ainda não força uma distribuição
específica de cenário; cada status de falha recebe o perfil realista e
compatível de TASK-DATA-004. Aqui são aplicados approval_rate_multiplier,
latency_p95_multiplier e timeout_rate.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from random import Random
from typing import Any

from app.simulation.config import GeneratorConfig
from app.simulation.outcomes import GeneratedAttempt, OutcomeGenerator
from app.simulation.scenario_contract import ScenarioDefinition
from app.streaming.server import TransactionPublisher


@dataclass(frozen=True)
class InjectionResult:
    scenario_id: str
    correlation_id: str
    events_published: int
    matched_attempts: int


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
    """Publica trafego normal e cenarios no mesmo servidor transacional."""

    def __init__(
        self,
        config: GeneratorConfig,
        publisher: TransactionPublisher,
        *,
        reference_time: datetime | None = None,
    ) -> None:
        self._config = config
        self._publisher = publisher
        self._generator = OutcomeGenerator(config, reference_time=reference_time)
        self._random = Random(config.seed ^ 0xC0FFEE)

    def emit_baseline_batch(self, payment_count: int) -> int:
        """Publica trafego normal; a ingestão o recebe pelo listener separado."""
        events: list[dict[str, Any]] = []
        for attempts in self._generator.generate_payments(payment_count):
            events.extend(self._generator.to_canonical_events(attempts))
        return self._publisher.publish(events).accepted

    def inject_scenario(self, scenario: ScenarioDefinition, *, payment_count: int = 50) -> InjectionResult:
        """Gera `payment_count` payments; nas tentativas que casam `scenario.filters`,
        reamostra o status e escala a latencia pelos `effects` de CTR-SCN-001;
        publica matched e nao-matched para o listener de ingestão."""
        matched = 0
        events: list[dict[str, Any]] = []
        latency_multiplier = scenario.effects.get("latency_p95_multiplier")

        for attempts in self._generator.generate_payments(payment_count):
            adjusted: list[GeneratedAttempt] = []
            matched_flags: list[bool] = []
            for attempt in attempts:
                is_match = _matches_filters(attempt.context, scenario.filters)
                matched_flags.append(is_match)
                if is_match:
                    matched += 1
                    # A changed status cannot retain a decline selected for the
                    # original outcome. OutcomeGenerator picks a compatible code
                    # when materializing the adjusted canonical event.
                    attempt = replace(
                        attempt,
                        status=_resample_status(self._random, attempt.status, scenario.effects),
                        decline=None,
                    )
                adjusted.append(attempt)

            for attempt, event, is_match in zip(adjusted, self._generator.to_canonical_events(adjusted), matched_flags):
                if is_match:
                    event = _apply_latency_effect(event, latency_multiplier)
                    event["correlation_id"] = f"demo:{scenario.scenario_id}"
                events.append(event)

        receipt = self._publisher.publish(events)

        return InjectionResult(
            scenario_id=scenario.scenario_id,
            correlation_id=f"demo:{scenario.scenario_id}",
            events_published=receipt.accepted,
            matched_attempts=matched,
        )
