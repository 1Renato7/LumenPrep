from __future__ import annotations

from app.aggregation import get_current_metrics
from app.ingestion import ingest_event


def test_cube_preserves_all_pre_outcome_dimensions_and_decline_evidence(valid_attempt):
    failed = dict(valid_attempt)
    failed.update(
        event_id="cube-failed",
        attempt_id="cube-failed",
        payment_id="cube-failed",
        merchant_id="merchant_br_aurora",
        provider_id="stripe",
        country="BR",
        payment_method_category="CARD",
        status="DECLINED",
        decline={
            "normalized_code": "ISSUER_UNAVAILABLE",
            "category": "ISSUER",
            "retryability": "RETRY_LATER",
            "raw_code": "91",
            "raw_message": "Issuer unavailable",
            "mapping_version": "1.0",
        },
        card={"brand": "VISA", "type": "CREDIT", "issuer_bank_id": "itau_br", "issuer_country": "BR", "bin_prefix": None},
    )
    approved = dict(failed, event_id="cube-approved", attempt_id="cube-approved", payment_id="cube-approved", status="SUCCEEDED", decline=None)
    assert ingest_event(failed).status == "ACCEPTED"
    assert ingest_event(approved).status == "ACCEPTED"

    slice_values = {
        "merchant_id": "merchant_br_aurora",
        "provider_id": "stripe",
        "payment_method_category": "CARD",
        "country": "BR",
        "issuer_bank_id": "itau_br",
    }
    windows = get_current_metrics(dimensions=slice_values)

    assert len(windows) == 1
    assert windows[0].dimensions == {**slice_values, "currency": "BRL"}
    assert windows[0].eligible_attempts == 2
    assert windows[0].decline_profile == {"ISSUER_UNAVAILABLE": 1, "NO_DECLINE": 1}
