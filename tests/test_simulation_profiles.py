from datetime import datetime, timezone
from pathlib import Path

from app.simulation import GeneratedAttempt, HistoricalTransactionGenerator, OutcomeGenerator, load_generator_config


CONFIG_PATH = Path("config/generator/v1/default.json")
REFERENCE_TIME = datetime(2026, 8, 29, 14, 0, 0, tzinfo=timezone.utc)


def _generator() -> OutcomeGenerator:
    return OutcomeGenerator(load_generator_config(CONFIG_PATH), reference_time=REFERENCE_TIME)


def _attempt(provider_id: str, status: str, *, sequence: int) -> GeneratedAttempt:
    return GeneratedAttempt(
        payment_id=f"pay_{sequence}",
        attempt_id=f"att_{sequence}",
        attempt_sequence=1,
        context={
            "country": "BR",
            "merchant_id": "merchant_aurora",
            "provider_id": provider_id,
            "payment_method_category": "CARD",
            "status": status,
        },
        status=status,
    )


def _percentile(values: list[int], quantile: float) -> int:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * quantile)]


def test_latency_profiles_are_reproducible_and_keep_provider_p95_ordering():
    first = _generator()
    second = _generator()
    profiles: dict[str, tuple[int, int]] = {}

    for provider in ("stripe", "adyen", "dlocal"):
        first_values = [
            first._to_canonical(_attempt(provider, "SUCCEEDED", sequence=index), REFERENCE_TIME)["timing"]
            for index in range(1, 1001)
        ]
        second_values = [
            second._to_canonical(_attempt(provider, "SUCCEEDED", sequence=index), REFERENCE_TIME)["timing"]
            for index in range(1, 1001)
        ]
        assert first_values == second_values
        provider_latencies = [timing["provider_latency_ms"] for timing in first_values]
        profiles[provider] = (_percentile(provider_latencies, 0.5), _percentile(provider_latencies, 0.95))
        assert all(timing["total_latency_ms"] == timing["provider_latency_ms"] + timing["orchestrator_latency_ms"] for timing in first_values)

    assert profiles["stripe"][0] < profiles["adyen"][0] < profiles["dlocal"][0]
    assert profiles["stripe"][1] < profiles["adyen"][1] < profiles["dlocal"][1]


def test_failure_statuses_receive_only_compatible_decline_codes_and_unknown_provider_uses_fallback():
    generator = _generator()
    supported = {
        "DECLINED": {"DO_NOT_HONOR", "INSUFFICIENT_FUNDS", "SUSPECTED_FRAUD", "TRANSACTION_NOT_PERMITTED", "CARD_RESTRICTED"},
        "TIMEOUT": {"PROVIDER_TIMEOUT"},
        "ERROR": {"PROVIDER_INTERNAL_ERROR"},
    }

    for sequence, status in enumerate(("SUCCEEDED", "DECLINED", "TIMEOUT", "ERROR"), start=1):
        event = generator._to_canonical(_attempt("new-provider", status, sequence=sequence), REFERENCE_TIME)
        if status == "SUCCEEDED":
            assert "decline" not in event
            continue
        assert event["decline"]["normalized_code"] in supported[status]
        assert event["decline"]["raw_code"]
        assert event["decline"]["raw_message"]


def test_historical_low_sample_batch_keeps_latency_and_decline_data_without_ground_truth():
    generator = HistoricalTransactionGenerator(load_generator_config(CONFIG_PATH), start_at=REFERENCE_TIME)
    batches = list(generator.iter_batches(transactions_per_minute=8, batch_minutes=30, total_minutes=120))
    low_sample = next(batch for batch in batches if batch.is_low_sample)

    assert len(low_sample.events) >= 12
    assert all("ground_truth" not in event for event in low_sample.events)
    assert all(event["timing"]["total_latency_ms"] >= event["timing"]["provider_latency_ms"] for event in low_sample.events)
    for event in low_sample.events:
        if event["status"] in {"DECLINED", "TIMEOUT", "ERROR"}:
            assert event["decline"]["mapping_version"] == "generator-v1"
