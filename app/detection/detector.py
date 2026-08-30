"""Seasonal anomaly detection for CTR-AGG-001 windows.

The detector is intentionally statistical only: it emits metric candidates and
never attributes a cause. Incident correlation and RCA remain downstream.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from hashlib import sha256
import json
from math import erf, sqrt
from statistics import median

from app.aggregation import WindowMetrics

from .models import AnomalyCandidate, DetectionSignal, SeasonalBaseline

DETECTOR_VERSION = "1.0"
_Z_95 = 1.959963984540054


def build_seasonal_baseline(
    history: Iterable[WindowMetrics],
    current: WindowMetrics,
    *,
    low_sample_attempts: int,
    sample_field: str = "eligible_attempts",
) -> SeasonalBaseline | None:
    """Pool a slice by weekday/hour, then hour, then globally.

    Only windows before ``current`` are eligible, preventing future leakage when
    callers pass a full ordered series. Every selected pool must meet the same
    configured low-volume guard used for the observed window.
    """

    _require_positive_threshold(low_sample_attempts)
    current_time = _parse_timestamp(current.window_start)
    same_slice = [
        window
        for window in history
        if window.dimensions == current.dimensions and _parse_timestamp(window.window_start) < current_time
    ]
    if not same_slice:
        return None

    exact = [
        window
        for window in same_slice
        if _parse_timestamp(window.window_start).weekday() == current_time.weekday()
        and _parse_timestamp(window.window_start).hour == current_time.hour
    ]
    hour = [window for window in same_slice if _parse_timestamp(window.window_start).hour == current_time.hour]
    for pooling_level, pool in (("weekday_hour", exact), ("hour", hour), ("global", same_slice)):
        sample_size = sum(int(getattr(window, sample_field)) for window in pool)
        if sample_size >= low_sample_attempts:
            return _baseline_from_pool(pool, sample_size, pooling_level, sample_field=sample_field)
    return None


def approval_rate_signal(current: WindowMetrics, baseline: SeasonalBaseline) -> DetectionSignal | None:
    """Detect an approval drop when the 95% Wilson upper bound remains below expected."""

    observed = current.approval_rate
    if _wilson_bound(observed, current.eligible_attempts, upper=True) >= baseline.approval_rate:
        return None
    return DetectionSignal(
        metric="APPROVAL_RATE",
        observed=observed,
        expected=baseline.approval_rate,
        statistical_strength=_binomial_strength(observed, baseline.approval_rate, current.eligible_attempts),
    )


def payment_conversion_signal(current: WindowMetrics, baseline: SeasonalBaseline) -> DetectionSignal | None:
    """Detect an operationally material conversion drop per unique payment.

    A fifteen percentage point guard avoids escalating a statistically visible
    but operationally irrelevant wobble.  The Wilson bound uses payment IDs as
    Bernoulli observations, deliberately excluding retry inflation.
    """
    observed = current.payment_conversion
    if baseline.payment_conversion - observed < 0.15:
        return None
    if _wilson_bound(observed, current.unique_payments, upper=True) >= baseline.payment_conversion:
        return None
    return DetectionSignal(
        metric="PAYMENT_CONVERSION",
        observed=observed,
        expected=baseline.payment_conversion,
        statistical_strength=_binomial_strength(observed, baseline.payment_conversion, current.unique_payments),
    )


def latency_p95_signal(current: WindowMetrics, baseline: SeasonalBaseline) -> DetectionSignal | None:
    """Detect a robust p95 increase using a three-MAD threshold."""

    scale = max(baseline.latency_p95_mad, baseline.latency_p95_ms * 0.05, 1.0)
    observed = current.latency_p95_ms
    if observed <= baseline.latency_p95_ms + 3 * scale:
        return None
    return DetectionSignal(
        metric="LATENCY_P95",
        observed=observed,
        expected=baseline.latency_p95_ms,
        statistical_strength=_normal_cdf((observed - baseline.latency_p95_ms) / scale),
    )


def timeout_rate_signal(current: WindowMetrics, baseline: SeasonalBaseline) -> DetectionSignal | None:
    """Detect a timeout-rate increase when the 95% Wilson lower bound exceeds expected."""

    observed = current.timeout_rate
    if _wilson_bound(observed, current.eligible_attempts, upper=False) <= baseline.timeout_rate:
        return None
    return DetectionSignal(
        metric="TIMEOUT_RATE",
        observed=observed,
        expected=baseline.timeout_rate,
        statistical_strength=_binomial_strength(observed, baseline.timeout_rate, current.eligible_attempts),
    )


def to_anomaly_candidate(
    signal: DetectionSignal,
    current: WindowMetrics,
    baseline: SeasonalBaseline,
    *,
    detector_version: str = DETECTOR_VERSION,
) -> AnomalyCandidate:
    """Convert a statistical signal into the frozen CTR-DET-001 payload."""

    effect_absolute = signal.observed - signal.expected
    effect_relative = effect_absolute / abs(signal.expected) if signal.expected else (1.0 if effect_absolute else 0.0)
    lost_approvals = (
        max(signal.expected - signal.observed, 0.0) * current.eligible_attempts
        if signal.metric == "APPROVAL_RATE"
        else 0.0
    )
    estimated_lost_conversions = (
        max(signal.expected - signal.observed, 0.0) * current.unique_payments
        if signal.metric == "PAYMENT_CONVERSION"
        else 0.0
    )
    expected_approvals = signal.expected * current.eligible_attempts
    loss_coverage = min(lost_approvals / expected_approvals, 1.0) if expected_approvals else 0.0
    candidate_key = json.dumps(
        {
            "correlation_id": current.correlation_id,
            "window_start": current.window_start,
            "window_end": current.window_end,
            "slice": current.dimensions,
            "metric": signal.metric,
            "pooling_level": baseline.pooling_level,
            "detector_version": detector_version,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return AnomalyCandidate(
        candidate_id=f"det_{sha256(candidate_key.encode('utf-8')).hexdigest()[:16]}",
        window={"start": current.window_start, "end": current.window_end},
        slice=dict(current.dimensions),
        metric=signal.metric,
        observed=signal.observed,
        expected=signal.expected,
        sample_size=current.unique_payments if signal.metric == "PAYMENT_CONVERSION" else current.eligible_attempts,
        effect_absolute=effect_absolute,
        effect_relative=effect_relative,
        statistical_strength=_unit_interval(signal.statistical_strength),
        lost_approvals=lost_approvals,
        estimated_lost_conversions=estimated_lost_conversions,
        loss_coverage=_unit_interval(loss_coverage),
        temporal_consistency=_unit_interval(baseline.window_count / 3),
        data_quality=_unit_interval(current.data_quality),
        evidence_refs=[
            f"window://{current.correlation_id}",
            f"baseline://{baseline.pooling_level}/{baseline.window_count}-windows",
        ],
        detector_version=detector_version,
        correlation_id=current.correlation_id,
        schema_version="2.0" if signal.metric == "PAYMENT_CONVERSION" else "1.0",
    )


def detect_candidates(
    windows: Iterable[WindowMetrics],
    *,
    low_sample_attempts: int,
    detector_version: str = DETECTOR_VERSION,
) -> list[AnomalyCandidate]:
    """Evaluate an arbitrary iterable chronologically without changing its source API."""

    _require_positive_threshold(low_sample_attempts)
    ordered = sorted(windows, key=lambda window: _parse_timestamp(window.window_start))
    candidates: list[AnomalyCandidate] = []
    history: list[WindowMetrics] = []
    for current in ordered:
        if current.eligible_attempts >= low_sample_attempts:
            baseline = build_seasonal_baseline(history, current, low_sample_attempts=low_sample_attempts)
            if baseline is not None:
                for signal in (
                    approval_rate_signal(current, baseline),
                    latency_p95_signal(current, baseline),
                    timeout_rate_signal(current, baseline),
                ):
                    if signal is not None:
                        candidates.append(
                            to_anomaly_candidate(
                                signal,
                                current,
                                baseline,
                                detector_version=detector_version,
                            )
                        )
        history.append(current)
    return candidates


def detect_payment_conversion_candidates(
    windows: Iterable[WindowMetrics], *, minimum_unique_payments: int = 10,
    detector_version: str = DETECTOR_VERSION,
) -> list[AnomalyCandidate]:
    """Run the conversion detector independently from attempt-rate signals."""
    _require_positive_threshold(minimum_unique_payments)
    ordered = sorted(windows, key=lambda window: _parse_timestamp(window.window_start))
    history: list[WindowMetrics] = []
    candidates: list[AnomalyCandidate] = []
    for current in ordered:
        if current.unique_payments >= minimum_unique_payments:
            baseline = build_seasonal_baseline(
                history, current, low_sample_attempts=minimum_unique_payments, sample_field="unique_payments"
            )
            if baseline is not None and baseline.window_count >= 3:
                signal = payment_conversion_signal(current, baseline)
                if signal is not None:
                    candidates.append(to_anomaly_candidate(signal, current, baseline, detector_version=detector_version))
        history.append(current)
    return candidates


def _baseline_from_pool(
    pool: list[WindowMetrics], sample_size: int, pooling_level: str, *, sample_field: str = "eligible_attempts"
) -> SeasonalBaseline:
    def weighted_rate(name: str) -> float:
        return sum(getattr(window, name) * int(getattr(window, sample_field)) for window in pool) / sample_size

    latencies = [window.latency_p95_ms for window in pool]
    latency_p95 = median(latencies)
    return SeasonalBaseline(
        approval_rate=weighted_rate("approval_rate"),
        payment_conversion=weighted_rate("payment_conversion"),
        latency_p95_ms=latency_p95,
        latency_p95_mad=median([abs(value - latency_p95) for value in latencies]),
        timeout_rate=weighted_rate("timeout_rate"),
        sample_size=sample_size,
        window_count=len(pool),
        pooling_level=pooling_level,
    )


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _wilson_bound(rate: float, sample_size: int, *, upper: bool) -> float:
    if sample_size <= 0:
        return 1.0 if upper else 0.0
    successes = round(rate * sample_size)
    proportion = successes / sample_size
    denominator = 1 + _Z_95**2 / sample_size
    centre = proportion + _Z_95**2 / (2 * sample_size)
    margin = _Z_95 * sqrt(
        proportion * (1 - proportion) / sample_size + _Z_95**2 / (4 * sample_size**2)
    )
    return (centre + margin if upper else centre - margin) / denominator


def _binomial_strength(observed: float, expected: float, sample_size: int) -> float:
    variance = max(expected * (1 - expected) / sample_size, 1 / sample_size**2)
    return _normal_cdf(abs(observed - expected) / sqrt(variance))


def _normal_cdf(value: float) -> float:
    return 0.5 * (1 + erf(value / sqrt(2)))


def _unit_interval(value: float) -> float:
    return max(0.0, min(1.0, value))


def _require_positive_threshold(low_sample_attempts: int) -> None:
    if isinstance(low_sample_attempts, bool) or low_sample_attempts <= 0:
        raise ValueError("low_sample_attempts must be a positive integer")
