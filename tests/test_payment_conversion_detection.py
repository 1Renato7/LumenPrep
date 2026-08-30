from datetime import datetime, timedelta, timezone

from app.aggregation import WindowMetrics
from app.detection import detect_payment_conversion_candidates


def _observation(hour: int, conversion: float, payments: int = 20) -> WindowMetrics:
    start = datetime(2026, 8, 30, hour, tzinfo=timezone.utc)
    return WindowMetrics(
        window_start=start.isoformat().replace("+00:00", "Z"), window_end=(start + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
        dimensions={"provider_id": "ADYEN", "currency": "BRL"}, eligible_attempts=payments + 8,
        approved_attempts=round((payments + 8) * conversion), unique_payments=payments,
        approved_payments=round(payments * conversion), amount_minor=1000, currency="BRL",
        approval_rate=conversion, payment_conversion=conversion, latency_p50_ms=10, latency_p95_ms=20,
        timeout_rate=0, decline_counts={}, decline_profile={}, data_quality=1, window_revision=1, correlation_id="corr_conversion",
    )


def test_conversion_drop_uses_unique_payments_and_prior_baseline_only() -> None:
    # The final observation is the only drop; later recovery must not change its baseline.
    windows = [_observation(hour, 0.9) for hour in range(3)] + [_observation(3, 0.5)] + [_observation(4, 0.98)]
    candidates = detect_payment_conversion_candidates(windows)
    drop = [candidate for candidate in candidates if candidate.window["start"].startswith("2026-08-30T03")]
    assert len(drop) == 1
    assert drop[0].metric == "PAYMENT_CONVERSION"
    assert drop[0].sample_size == 20
    assert drop[0].estimated_lost_conversions == 8.0


def test_conversion_requires_ten_unique_payments() -> None:
    candidates = detect_payment_conversion_candidates([_observation(hour, 0.9) for hour in range(3)] + [_observation(3, 0.2, 9)])
    assert candidates == []
