"""Fixture-first tests for TASK-DET-001..004 / LUM2-50..53."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from math import isclose
from pathlib import Path

from jsonschema import Draft202012Validator

from app.aggregation import WindowMetrics
from app.detection import build_seasonal_baseline, detect_candidates


ROOT = Path(__file__).resolve().parent.parent
LOW_SAMPLE_ATTEMPTS = 12  # config/generator/v1/default.json volume.low_sample_attempts


def _window(
    start: datetime,
    *,
    attempts: int = 100,
    approval_rate: float = 0.90,
    latency_p95_ms: float = 100.0,
    timeout_rate: float = 0.01,
    correlation_id: str | None = None,
) -> WindowMetrics:
    return WindowMetrics(
        window_start=start.isoformat().replace("+00:00", "Z"),
        window_end=(start + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        dimensions={"provider_id": "stripe", "country": "BR"},
        eligible_attempts=attempts,
        approved_attempts=round(attempts * approval_rate),
        unique_payments=attempts,
        approved_payments=round(attempts * approval_rate),
        amount_minor=attempts * 100,
        currency="BRL",
        approval_rate=approval_rate,
        payment_conversion=approval_rate,
        latency_p50_ms=latency_p95_ms * 0.6,
        latency_p95_ms=latency_p95_ms,
        timeout_rate=timeout_rate,
        decline_counts={"GENERIC": attempts - round(attempts * approval_rate)},
        data_quality=0.98,
        window_revision=1,
        correlation_id=correlation_id or f"corr-{start.date().isoformat()}",
    )


def _seasonal_history() -> list[WindowMetrics]:
    start = datetime(2026, 7, 6, 10, tzinfo=timezone.utc)  # Monday, 10:00 UTC
    return [_window(start + timedelta(weeks=index), correlation_id=f"corr-history-{index}") for index in range(4)]


def test_baseline_pools_weekday_hour_then_falls_back_to_hour() -> None:
    current = _window(datetime(2026, 8, 3, 10, tzinfo=timezone.utc), attempts=20)
    history = [
        _window(datetime(2026, 7, 27, 10, tzinfo=timezone.utc), attempts=6),
        _window(datetime(2026, 7, 28, 10, tzinfo=timezone.utc), attempts=10),
        _window(datetime(2026, 7, 29, 10, tzinfo=timezone.utc), attempts=10),
    ]

    baseline = build_seasonal_baseline(history, current, low_sample_attempts=LOW_SAMPLE_ATTEMPTS)

    assert baseline is not None
    assert baseline.pooling_level == "hour"
    assert baseline.sample_size == 26
    assert isclose(baseline.approval_rate, 0.90)


def test_known_injected_anomaly_emits_three_statistical_candidates() -> None:
    anomaly = _window(
        datetime(2026, 8, 3, 10, tzinfo=timezone.utc),
        approval_rate=0.60,
        latency_p95_ms=200.0,
        timeout_rate=0.10,
        correlation_id="corr-injected-anomaly",
    )

    candidates = detect_candidates([*_seasonal_history(), anomaly], low_sample_attempts=LOW_SAMPLE_ATTEMPTS)

    assert {candidate.metric for candidate in candidates} == {"APPROVAL_RATE", "LATENCY_P95", "TIMEOUT_RATE"}
    approval = next(candidate for candidate in candidates if candidate.metric == "APPROVAL_RATE")
    assert isclose(approval.lost_approvals, 30.0)
    assert isclose(approval.effect_absolute, -0.30)
    assert all(candidate.correlation_id == "corr-injected-anomaly" for candidate in candidates)


def test_normal_series_and_low_volume_window_do_not_alert() -> None:
    normal = _window(datetime(2026, 8, 3, 10, tzinfo=timezone.utc), correlation_id="corr-normal")
    low_volume_anomaly = _window(
        datetime(2026, 8, 10, 10, tzinfo=timezone.utc),
        attempts=LOW_SAMPLE_ATTEMPTS - 1,
        approval_rate=0.0,
        latency_p95_ms=500.0,
        timeout_rate=1.0,
        correlation_id="corr-low-volume",
    )

    assert detect_candidates([*_seasonal_history(), normal, low_volume_anomaly], low_sample_attempts=LOW_SAMPLE_ATTEMPTS) == []


def test_candidate_output_validates_against_ctr_det_schema() -> None:
    anomaly = _window(
        datetime(2026, 8, 3, 10, tzinfo=timezone.utc),
        approval_rate=0.60,
        latency_p95_ms=200.0,
        timeout_rate=0.10,
    )
    schema = json.loads((ROOT / "contracts" / "v1" / "anomaly-candidate.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    candidates = detect_candidates([*_seasonal_history(), anomaly], low_sample_attempts=LOW_SAMPLE_ATTEMPTS)

    assert candidates
    for candidate in candidates:
        assert list(validator.iter_errors(candidate.model_dump())) == []


def test_candidate_identity_separates_currencies_in_same_correlation_and_window() -> None:
    brl_history = [window.model_copy(update={"dimensions": {**window.dimensions, "currency": "BRL"}}) for window in _seasonal_history()]
    mxn_history = [
        window.model_copy(
            update={
                "dimensions": {**window.dimensions, "currency": "MXN"},
                "currency": "MXN",
            }
        )
        for window in _seasonal_history()
    ]
    start = datetime(2026, 8, 3, 10, tzinfo=timezone.utc)
    anomaly = _window(
        start,
        approval_rate=0.60,
        latency_p95_ms=200.0,
        timeout_rate=0.10,
        correlation_id="corr-mixed-currency",
    )
    brl = anomaly.model_copy(update={"dimensions": {**anomaly.dimensions, "currency": "BRL"}})
    mxn = anomaly.model_copy(
        update={"dimensions": {**anomaly.dimensions, "currency": "MXN"}, "currency": "MXN"}
    )

    candidates = detect_candidates(
        [*brl_history, *mxn_history, brl, mxn],
        low_sample_attempts=LOW_SAMPLE_ATTEMPTS,
    )

    assert len(candidates) == 6
    assert len({candidate.candidate_id for candidate in candidates}) == 6
    assert {candidate.slice["currency"] for candidate in candidates} == {"BRL", "MXN"}
