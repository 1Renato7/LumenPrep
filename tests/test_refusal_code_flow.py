from app.agent.evidence import build_evidence_pack
from app.api.transactions import TransactionInput
from app.ingestion.storage import get_connection
from app.incidents import Incident
from app.worker.transaction_worker import _generate_outcome


def _input(code: str) -> dict:
    return TransactionInput(
        merchant_id="merchant_br_01", provider_id="adyen", issuer_bank="nubank_br",
        country="BR", currency="BRL", amount_minor=12990, payment_method_category="CARD",
        card_brand="VISA", card_type="CREDIT", provider_response_code=code,
    ).model_dump(mode="json")


def test_mapped_response_code_is_persistable_transaction_fact():
    # Opening the connection seeds the versioned local reference table.
    get_connection()
    adapted = _generate_outcome("txn_refusal_51", _input("51"), "corr_refusal")

    assert adapted.result == "FAILED"
    assert adapted.outcome["provider_response_code"] == "51"
    assert adapted.classification["reason"] == "Insufficient funds"
    assert adapted.classification["refusal_resolution"]["lookup_status"] == "MATCH_FOUND"
    assert adapted.event["decline"]["raw_message"] == "Insufficient funds"


def test_unknown_response_code_stays_unknown_without_invented_reason():
    get_connection()
    adapted = _generate_outcome("txn_refusal_unknown", _input("99999"), "corr_refusal")

    assert adapted.result == "UNKNOWN"
    assert adapted.classification["refusal_resolution"]["lookup_status"] == "NOT_FOUND"
    assert adapted.classification["refusal_resolution"]["reason"] is None


def test_refusal_summary_is_explicit_agent_evidence_not_database_access():
    incident = Incident.model_validate({
        "incident_id": "inc_refusal", "correlation_id": "corr_refusal", "estimated_started_at": "2026-08-30T12:00:00Z",
        "detected_at": "2026-08-30T12:05:00Z", "title": "Refusal spike", "scope": {"provider_id": ["adyen"]}, "metrics": {},
        "impact": {"metric": "GMV_AT_RISK", "method": "EXPECTED_APPROVAL_SHORTFALL", "amount_minor": 0, "currency": "BRL"},
        "root_cause": {"status": "INCONCLUSIVE", "category": None, "confidence": 0.0, "confidence_factors": {}, "alternatives": []},
        "state": "INCONCLUSIVE", "evidence": [], "recommendations": [], "limitations": [],
    })
    summary = {"provider_id": "ADYEN", "card_brand": "VISA", "response_code": "51", "reason": "Insufficient funds",
               "source": "ADYEN_RAW_ACQUIRER", "mapping_version": "2026.08.30", "transaction_count": 17,
               "evidence_id": "evd_refusal_51"}
    pack = build_evidence_pack(incident, decline_profile={"RESPONSE_CODE_51": 17}, refusal_code_summaries=[summary])

    assert pack.refusal_code_summaries[0].reason == "Insufficient funds"
    assert "evd_refusal_51" in pack.authorized_evidence_ids
    assert all("connection" not in field.lower() for field in pack.model_dump())
