from __future__ import annotations

from copy import deepcopy

from app.evaluation.provenance import audit_terminal_transaction
from app.simulation.transaction_outcomes import adapt_transaction


def _record() -> tuple[dict, dict]:
    transaction_id = "txn-provenance-001"
    correlation_id = "corr-provenance-001"
    transaction_input = {
        "merchant_id": "merchant_br_01", "provider_id": "provider_alpha", "issuer_bank": "bank_br_a",
        "country": "BR", "currency": "BRL", "amount_minor": 12990, "payment_method_category": "CARD",
        "card_brand": "VISA", "card_type": "CREDIT", "channel": "WEB", "scenario_effects": {"timeout_rate": 1.0},
    }
    adapted = adapt_transaction(transaction_input, transaction_id=transaction_id, correlation_id=correlation_id)
    return {
        "transaction_id": transaction_id,
        "correlation_id": correlation_id,
        "input": transaction_input,
        "status": adapted.result,
        "outcome": adapted.outcome,
        "classification": adapted.classification,
    }, adapted.event


def test_provenance_auditor_accepts_an_error_with_matching_source_and_events():
    record, event = _record()

    audit = audit_terminal_transaction(record, raw_event=event, canonical_event=event)

    assert audit.passed is True
    assert audit.failures == ()


def test_provenance_auditor_rejects_an_invented_error_reason():
    record, event = _record()
    forged = deepcopy(record)
    forged["classification"]["reason"] = "The provider is certainly unavailable."

    audit = audit_terminal_transaction(forged, raw_event=event, canonical_event=event)

    assert audit.passed is False
    assert "classification.reason does not match the provider result" in audit.failures


def test_provenance_auditor_rejects_a_missing_durable_source_event():
    record, event = _record()

    audit = audit_terminal_transaction(record, raw_event=None, canonical_event=event)

    assert audit.passed is False
    assert "raw_event is missing" in audit.failures


def test_provenance_auditor_can_use_internal_source_input_without_exposing_a_scenario_control():
    record, event = _record()
    public_record = deepcopy(record)
    public_record["input"].pop("scenario_effects")

    audit = audit_terminal_transaction(
        public_record, source_input=record["input"], raw_event=event, canonical_event=event
    )

    assert audit.passed is True


def test_provenance_auditor_rejects_an_unaudited_classification_field():
    record, event = _record()
    forged = deepcopy(record)
    forged["classification"]["provider_story"] = "The provider was probably unavailable."

    audit = audit_terminal_transaction(forged, raw_event=event, canonical_event=event)

    assert audit.passed is False
    assert "classification has unaudited fields: ['provider_story']" in audit.failures
