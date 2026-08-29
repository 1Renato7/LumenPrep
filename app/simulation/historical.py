"""TASK-DATA-004: deterministic, seasonal historical transaction producer."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np

from app.simulation.config import GeneratorConfig, WeightedValue
from app.streaming.server import TransactionPublisher

_CURRENCY_BY_COUNTRY = {"BR": "BRL", "MX": "MXN", "CO": "COP"}
_WEEKDAY_MULTIPLIERS = np.array((0.83, 1.03, 1.06, 1.08, 1.12, 0.91, 0.76))


@dataclass(frozen=True)
class HistoricalBatch:
    start_at: datetime
    end_at: datetime
    events: tuple[dict[str, Any], ...]
    is_low_sample: bool


@dataclass(frozen=True)
class HistoricalGenerationReport:
    seed: int
    start_at: str
    end_at: str
    generated_events: int
    published_events: int
    low_sample_start_at: str


class HistoricalTransactionGenerator:
    """Generates normal traffic with hour, weekday, trend and low-sample effects.

    Sampling and volume calculations are vectorized per batch. Payload materialization
    is intentionally streamed so a 90-day run does not retain all transactions in RAM.
    """

    def __init__(self, config: GeneratorConfig, *, start_at: datetime) -> None:
        if start_at.tzinfo is None:
            raise ValueError("start_at must be timezone-aware")
        self._config = config
        self._start_at = start_at.astimezone(timezone.utc).replace(second=0, microsecond=0)
        self._random = np.random.default_rng(config.seed)
        self._sequence = 0

    def iter_batches(
        self,
        *,
        transactions_per_minute: int,
        batch_minutes: int = 60,
        total_minutes: int | None = None,
    ) -> Iterator[HistoricalBatch]:
        if transactions_per_minute <= 0:
            raise ValueError("transactions_per_minute must be positive")
        if batch_minutes <= 0:
            raise ValueError("batch_minutes must be positive")
        total_minutes = total_minutes if total_minutes is not None else self._config.days * 24 * 60
        if total_minutes <= 0 or total_minutes > self._config.days * 24 * 60:
            raise ValueError("total_minutes must be within the configured historical horizon")

        low_sample_minute = total_minutes // 2
        for offset in range(0, total_minutes, batch_minutes):
            minute_count = min(batch_minutes, total_minutes - offset)
            indices = np.arange(offset, offset + minute_count)
            counts = self._minute_counts(indices, transactions_per_minute, total_minutes)
            low_sample_position = np.where(indices == low_sample_minute)[0]
            if low_sample_position.size:
                counts[low_sample_position[0]] = self._config.low_sample_attempts
            event_minutes = np.repeat(indices, counts)
            events = self._events_for_minutes(event_minutes)
            batch_start = self._start_at + timedelta(minutes=offset)
            yield HistoricalBatch(
                start_at=batch_start,
                end_at=batch_start + timedelta(minutes=minute_count),
                events=tuple(events),
                is_low_sample=bool(low_sample_position.size),
            )

    def publish(
        self,
        publisher: TransactionPublisher,
        *,
        transactions_per_minute: int,
        batch_minutes: int = 60,
        total_minutes: int | None = None,
    ) -> HistoricalGenerationReport:
        generated = 0
        published = 0
        selected_minutes = total_minutes if total_minutes is not None else self._config.days * 24 * 60
        for batch in self.iter_batches(
            transactions_per_minute=transactions_per_minute,
            batch_minutes=batch_minutes,
            total_minutes=total_minutes,
        ):
            receipt = publisher.publish(batch.events)
            generated += len(batch.events)
            published += receipt.accepted
        end_at = self._start_at + timedelta(minutes=selected_minutes)
        low_sample_at = self._start_at + timedelta(minutes=selected_minutes // 2)
        return HistoricalGenerationReport(
            seed=self._config.seed,
            start_at=_iso_z(self._start_at),
            end_at=_iso_z(end_at),
            generated_events=generated,
            published_events=published,
            low_sample_start_at=_iso_z(low_sample_at),
        )

    def _minute_counts(self, indices: np.ndarray, rate: int, total_minutes: int) -> np.ndarray:
        absolute_minutes = self._start_at.weekday() * 24 * 60 + self._start_at.hour * 60 + self._start_at.minute + indices
        weekday = (absolute_minutes // (24 * 60)) % 7
        minute_of_day = absolute_minutes % (24 * 60)
        # Two broad demand peaks (business hours and evening) plus weekdays.
        hour = minute_of_day / 60.0
        hour_profile = 0.48 + 0.42 * np.exp(-((hour - 13.0) / 4.0) ** 2) + 0.24 * np.exp(
            -((hour - 20.0) / 3.0) ** 2
        )
        trend = 0.90 + 0.20 * (indices / max(total_minutes - 1, 1))
        expected = rate * hour_profile * _WEEKDAY_MULTIPLIERS[weekday] * trend
        return self._random.poisson(expected).astype(int)

    def _events_for_minutes(self, event_minutes: np.ndarray) -> list[dict[str, Any]]:
        count = int(event_minutes.size)
        if count == 0:
            return []
        dimensions = self._sample_dimensions(count)
        seconds = self._random.integers(0, 60, size=count)
        amounts = self._random.lognormal(mean=10.2, sigma=0.75, size=count).round().astype(int)
        provider_latencies = self._random.lognormal(mean=6.2, sigma=0.42, size=count).round().astype(int)
        slow = np.isin(dimensions["status"], ("TIMEOUT", "ERROR"))
        provider_latencies[slow] *= 4
        total_latencies = provider_latencies + self._random.integers(10, 80, size=count)

        events: list[dict[str, Any]] = []
        for index in range(count):
            self._sequence += 1
            event_time = self._start_at + timedelta(minutes=int(event_minutes[index]), seconds=int(seconds[index]))
            status = str(dimensions["status"][index])
            country = str(dimensions["country"][index])
            event: dict[str, Any] = {
                "schema_version": "1.0",
                "event_id": f"hist_evt_{int(self._start_at.timestamp())}_{self._sequence:09d}",
                "event_type": "PAYMENT_ATTEMPT_CREATED",
                "event_time": _iso_z(event_time),
                "received_at": _iso_z(event_time),
                "payment_id": f"hist_pay_{int(self._start_at.timestamp())}_{self._sequence:09d}",
                "attempt_id": f"hist_att_{int(self._start_at.timestamp())}_{self._sequence:09d}",
                "attempt_sequence": 1,
                "merchant_id": str(dimensions["merchant_id"][index]),
                "provider_id": str(dimensions["provider_id"][index]),
                "country": country,
                "currency": _CURRENCY_BY_COUNTRY.get(country, "USD"),
                "amount_minor": max(1, int(amounts[index])),
                "payment_method_category": str(dimensions["payment_method_category"][index]),
                "status": status,
                "timing": {
                    "provider_latency_ms": int(provider_latencies[index]),
                    "total_latency_ms": int(total_latencies[index]),
                },
                "correlation_id": f"history:{self._config.fingerprint[:12]}",
                "is_test": True,
            }
            if status == "DECLINED":
                event["decline"] = {
                    "normalized_code": "GENERIC_DECLINE",
                    "category": "PROVIDER",
                    "retryability": "RETRY_LATER",
                    "raw_code": None,
                    "raw_message": None,
                    "mapping_version": "historical-v1",
                }
            events.append(event)
        return events

    def _sample_dimensions(self, count: int) -> dict[str, np.ndarray]:
        sampled: dict[str, np.ndarray] = {}
        for dimension in self._config.sampling_order:
            values = self._sample_values(self._config.dimensions[dimension].values, count)
            matching_rules = [
                rule for rule in self._config.conditional_probabilities if rule.target_dimension == dimension
            ]
            # More specific rules win, matching GeneratorConfig.distribution_for.
            for rule in sorted(matching_rules, key=lambda item: len(item.when)):
                matches = np.ones(count, dtype=bool)
                for dependency, expected in rule.when.items():
                    matches &= sampled[dependency] == expected
                if matches.any():
                    values[matches] = self._sample_values(rule.values, int(matches.sum()))
            sampled[dimension] = values
        return sampled

    def _sample_values(self, values: tuple[WeightedValue, ...], count: int) -> np.ndarray:
        identifiers = np.array([value.identifier for value in values], dtype=object)
        probabilities = np.array([value.probability for value in values], dtype=float)
        return identifiers[self._random.choice(len(identifiers), size=count, p=probabilities)]


def _iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
