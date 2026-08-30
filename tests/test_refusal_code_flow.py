from app.agent.evidence import build_evidence_pack
from app.api.transactions import TransactionInput
from app.ingestion.storage import get_connection
from app.incidents import Incident
from app.refusal_codes.adyen_refusal_reasons import refusal_reason_options
from app.worker.transaction_worker import _generate_outcome


def _input(code: str) -> dict:
    return TransactionInput(
        merchant_id="merchant_br_01", provider_id="adyen", issuer_bank="nubank_br",
        country="BR", currency="BRL", amount_minor=12990, payment_method_category="CARD",
        card_brand="VISA", card_type="CREDIT", provider_response_code=code,
    ).model_dump(mode="json")


def _stripe_input(code: str) -> dict:
    payload = _input(code)
    payload.update({"provider_id": "stripe", "issuer_bank": "itau_br", "card_brand": "VISA"})
    return payload


def test_mapped_response_code_is_persistable_transaction_fact():
    # Opening the connection seeds the versioned local reference table.
    get_connection()
    adapted = _generate_outcome("txn_refusal_51", _input("51"), "corr_refusal")

    assert adapted.result == "FAILED"
    assert adapted.outcome["provider_response_code"] == "51"
    assert adapted.classification["reason"] == "Insufficient funds"
    assert adapted.classification["refusal_resolution"]["lookup_status"] == "MATCH_FOUND"
    assert adapted.classification["refusal_resolution"]["normalized_code"] == "INSUFFICIENT_FUNDS"
    assert adapted.outcome["normalized_decline_code"] == "INSUFFICIENT_FUNDS"
    assert adapted.classification["category"] == "ISSUER_DECLINE"
    assert adapted.event["decline"]["category"] == "ISSUER"
    assert adapted.event["decline"]["raw_message"] == "Insufficient funds"


def test_iso_8583_timeout_68_is_a_mapped_failure_not_an_unknown():
    get_connection()
    adapted = _generate_outcome("txn_refusal_68", _input("68"), "corr_refusal")

    assert adapted.result == "FAILED"
    assert adapted.outcome["normalized_decline_code"] == "PROVIDER_TIMEOUT"
    assert adapted.classification["refusal_resolution"]["lookup_status"] == "MATCH_FOUND"
    assert adapted.classification["refusal_resolution"]["source"] == "ISO_8583"


def test_unknown_response_code_stays_unknown_without_invented_reason():
    get_connection()
    adapted = _generate_outcome("txn_refusal_unknown", _input("99999"), "corr_refusal")

    assert adapted.result == "UNKNOWN"
    assert adapted.classification["refusal_resolution"]["lookup_status"] == "NOT_FOUND"
    assert adapted.classification["refusal_resolution"]["reason"] is None


def test_every_adyen_option_exposed_by_the_form_has_a_terminal_mapping():
    get_connection()

    for option in refusal_reason_options():
        adapted = _generate_outcome(f"txn_refusal_adyen_{option.code}", _input(option.code), "corr_refusal")

        assert adapted.result in {"SUCCEEDED", "FAILED"}
        assert adapted.classification["refusal_resolution"]["lookup_status"] == "MATCH_FOUND"
        assert adapted.classification["reason"] == option.reason


def test_stripe_lowercase_code_resolves_and_preserves_the_raw_provider_value():
    get_connection()
    adapted = _generate_outcome("txn_refusal_stripe", _stripe_input("do_not_honor"), "corr_refusal")

    assert adapted.result == "FAILED"
    assert adapted.outcome["normalized_decline_code"] == "DO_NOT_HONOR"
    assert adapted.event["decline"]["raw_code"] == "do_not_honor"
    assert adapted.classification["refusal_resolution"]["response_code"] == "DO_NOT_HONOR"


def test_acquirer_error_is_not_misclassified_as_an_issuer_decline():
    get_connection()
    adapted = _generate_outcome("txn_refusal_acquirer", _input("4"), "corr_refusal")

    assert adapted.result == "FAILED"
    assert adapted.outcome["normalized_decline_code"] == "ACQUIRER_ERROR"
    assert adapted.classification["category"] == "PROVIDER_ERROR"
    assert adapted.event["decline"]["category"] == "PROVIDER"


def test_issuer_unavailability_is_a_technical_timeout_not_an_issuer_decline():
    get_connection()
    adapted = _generate_outcome("txn_refusal_unavailable", _input("91"), "corr_refusal")

    assert adapted.result == "FAILED"
    assert adapted.outcome["normalized_decline_code"] == "ISSUER_UNAVAILABLE"
    assert adapted.classification["category"] == "TIMEOUT"
    assert adapted.event["decline"]["category"] == "TECHNICAL"


def test_refusal_summary_is_explicit_agent_evidence_not_database_access():
    incident = Incident.model_validate({
        "incident_id": "inc_refusal", "correlation_id": "corr_refusal", "estimated_started_at": "2026-08-30T12:00:00Z",
        "detected_at": "2026-08-30T12:05:00Z", "title": "Refusal spike", "scope": {"provider_id": ["adyen"]}, "metrics": {},
        "impact": {"metric": "GMV_AT_RISK", "method": "EXPECTED_APPROVAL_SHORTFALL", "amount_minor": 0, "currency": "BRL"},
        "root_cause": {"status": "INCONCLUSIVE", "category": None, "confidence": 0.0, "confidence_factors": {}, "alternatives": []},
        "state": "INCONCLUSIVE", "evidence": [], "recommendations": [], "limitations": [],
    })
    summary = {"provider_id": "ADYEN", "issuer_bank": "NUBANK_BR", "card_brand": "VISA", "response_code": "51", "normalized_code": "INSUFFICIENT_FUNDS", "reason": "Insufficient funds",
               "source": "ADYEN_RAW_ACQUIRER", "mapping_version": "2026.08.30", "transaction_count": 17,
               "evidence_id": "evd_refusal_51"}
    pack = build_evidence_pack(incident, decline_profile={"INSUFFICIENT_FUNDS": 17}, refusal_code_summaries=[summary])

    assert pack.refusal_code_summaries[0].reason == "Insufficient funds"
    assert "evd_refusal_51" in pack.authorized_evidence_ids
    assert all("connection" not in field.lower() for field in pack.model_dump())
