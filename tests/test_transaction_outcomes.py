import json
from pathlib import Path

from jsonschema import Draft202012Validator

from app.simulation.transaction_outcomes import adapt_transaction

ROOT = Path(__file__).resolve().parent.parent


def _input(**overrides: object) -> dict:
    payload = {
        "merchant_id": "merchant_br_01",
        "provider_id": "provider_alpha",
        "issuer_bank": "bank_br_a",
        "country": "BR",
        "currency": "BRL",
        "amount_minor": 12990,
        "payment_method_category": "CARD",
        "card_brand": "VISA",
        "card_type": "CREDIT",
        "provider_connection_id": "conn_br_primary",
        "channel": "WEB",
    }
    payload.update(overrides)
    return payload


def test_same_input_and_seed_context_produces_identical_adapter_payload():
    first = adapt_transaction(_input(), transaction_id="txn_adapter_001", correlation_id="corr_001")
    second = adapt_transaction(_input(), transaction_id="txn_adapter_001", correlation_id="corr_001")

    assert first == second
    assert "ground_truth" not in first.event
    assert "effect_multiplier" not in first.event


def test_adapter_covers_success_failure_and_honest_unknown():
    results = {
        adapt_transaction(_input(), transaction_id=f"txn_adapter_{index}", correlation_id="corr_001").result
        for index in range(300)
    }
    unknown = adapt_transaction(
        _input(payment_method_category="OTHER", card_brand=None, card_type=None),
        transaction_id="txn_adapter_other",
        correlation_id="corr_001",
    )

    assert {"SUCCEEDED", "FAILED"} <= results
    assert unknown.result == "UNKNOWN"
    assert unknown.classification["category"] == "UNKNOWN"
    assert unknown.outcome["normalized_decline_code"] is None


def test_adapter_event_conforms_to_ctr_evt_001():
    schema = json.loads((ROOT / "contracts" / "v1" / "canonical-attempt.schema.json").read_text(encoding="utf-8"))
    adapted = adapt_transaction(
        _input(card_type="NOT_APPLICABLE"), transaction_id="txn_adapter_schema", correlation_id="corr_001"
    )

    assert list(Draft202012Validator(schema).iter_errors(adapted.event)) == []
