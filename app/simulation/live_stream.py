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
from datetime import datetime, timedelta, timezone
from random import Random
from threading import Lock
from typing import Any

from app.simulation.config import GeneratorConfig
from app.simulation.outcomes import GeneratedAttempt, OutcomeGenerator
from app.simulation.scenario_contract import ScenarioDefinition
from app.streaming.server import TransactionPublisher


WINDOW_SECONDS = 300


@dataclass(frozen=True)
class InjectionResult:
    scenario_id: str
    correlation_id: str
    events_published: int
    matched_attempts: int


@dataclass(frozen=True)
class BaselineResult:
    window_count: int
    payments_requested: int
    events_published: int
    first_window_start: str
    last_window_end: str


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
        initial_time = reference_time or datetime(2026, 8, 29, 14, 0, 0, tzinfo=timezone.utc)
        if initial_time.tzinfo is None:
            raise ValueError("reference_time must include a timezone")
        self._generator = OutcomeGenerator(config, reference_time=initial_time)
        self._random = Random(config.seed ^ 0xC0FFEE)
        self._next_window_start = _window_start(initial_time)
        self._lock = Lock()

    def emit_baseline_batch(self, payment_count: int) -> int:
        """Compatibilidade para um único intervalo normal de cinco minutos."""
        return self.seed_baseline_history(window_count=1, payments_per_window=payment_count).events_published

    def seed_baseline_history(self, *, window_count: int, payments_per_window: int) -> BaselineResult:
        """Publica janelas normais consecutivas antes de uma injeção de cenário.

        O detector só pode comparar um cenário contra dados anteriores. Por isso
        todos os eventos de uma janela compartilham uma correlação de baseline e
        recebem timestamps distribuídos dentro do mesmo bucket de cinco minutos.
        """
        if window_count <= 0:
            raise ValueError("window_count must be positive")
        if payments_per_window <= 0:
            raise ValueError("payments_per_window must be positive")
        with self._lock:
            return self._seed_baseline_history(window_count=window_count, payments_per_window=payments_per_window)

    def _seed_baseline_history(self, *, window_count: int, payments_per_window: int) -> BaselineResult:
        first_window = self._next_window_start
        events_published = 0
        for _ in range(window_count):
            window_start = self._next_window_start
            correlation_id = f"demo:baseline:{int(window_start.timestamp())}"
            events = self._materialize_events(
                self._generator.generate_payments(payments_per_window),
                window_start=window_start,
                duration_seconds=WINDOW_SECONDS,
            )
            for event in events:
                event["correlation_id"] = correlation_id
            events_published += self._publisher.publish(events).accepted
            self._next_window_start += timedelta(seconds=WINDOW_SECONDS)

        return BaselineResult(
            window_count=window_count,
            payments_requested=window_count * payments_per_window,
            events_published=events_published,
            first_window_start=_iso_z(first_window),
            last_window_end=_iso_z(self._next_window_start),
        )

    def inject_scenario(self, scenario: ScenarioDefinition, *, payment_count: int = 50) -> InjectionResult:
        """Gera `payment_count` payments; nas tentativas que casam `scenario.filters`,
        reamostra o status e escala a latencia pelos `effects` de CTR-SCN-001;
        publica matched e nao-matched para o listener de ingestão."""
        with self._lock:
            return self._inject_scenario(scenario, payment_count=payment_count)

    def _inject_scenario(self, scenario: ScenarioDefinition, *, payment_count: int) -> InjectionResult:
        matched = 0
        pending_events: list[tuple[dict[str, Any], bool]] = []
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

            for event, is_match in zip(self._generator.to_canonical_events(adjusted), matched_flags):
                if is_match:
                    event = _apply_latency_effect(event, latency_multiplier)
                pending_events.append((event, is_match))

        materialized = self._materialize_existing_events(
            [event for event, _ in pending_events],
            window_start=self._next_window_start,
            duration_seconds=WINDOW_SECONDS,
        )
        events: list[dict[str, Any]] = []
        for event, (_, is_match) in zip(materialized, pending_events):
            if is_match:
                event["correlation_id"] = f"demo:{scenario.scenario_id}"
            events.append(event)

        receipt = self._publisher.publish(events)
        self._next_window_start += timedelta(seconds=WINDOW_SECONDS)

        return InjectionResult(
            scenario_id=scenario.scenario_id,
            correlation_id=f"demo:{scenario.scenario_id}",
            events_published=receipt.accepted,
            matched_attempts=matched,
        )

    def _materialize_events(
        self,
        payments: list[list[GeneratedAttempt]],
        *,
        window_start: datetime,
        duration_seconds: int,
    ) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for attempts in payments:
            events.extend(self._generator.to_canonical_events(attempts))
        return self._materialize_existing_events(events, window_start=window_start, duration_seconds=duration_seconds)

    @staticmethod
    def _materialize_existing_events(
        events: list[dict[str, Any]],
        *,
        window_start: datetime,
        duration_seconds: int,
    ) -> list[dict[str, Any]]:
        if not events:
            return []
        materialized: list[dict[str, Any]] = []
        for index, original in enumerate(events):
            event = dict(original)
            event_time = window_start + timedelta(seconds=(index * duration_seconds) // len(events))
            event_time_iso = _iso_z(event_time)
            event["event_time"] = event_time_iso
            event["received_at"] = event_time_iso
            materialized.append(event)
        return materialized


def _window_start(value: datetime) -> datetime:
    value = value.astimezone(timezone.utc)
    epoch = int(value.timestamp())
    return datetime.fromtimestamp(epoch - (epoch % WINDOW_SECONDS), tz=timezone.utc)


def _iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
