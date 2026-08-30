"""Guardrails of the proactive diagnostic agent (CTR-AGT-001..003).

Every test injects a fake suggestion client.  Nothing here reaches OpenAI, and
no test requires an API key: the agent's safety must be provable offline.
"""

from __future__ import annotations

import json
import sys
import types

import pytest

from app.agent import (
    AgentRetrievalTrace,
    DiagnosticAgentService,
    DiagnosticSuggestionRepository,
    OpenAISuggestionClient,
    TemplateSuggestionClient,
    build_evidence_pack,
    configured_suggestion_client,
)
from app.agent.prompt import system_prompt
from app.agent.service import MINIMUM_INDEPENDENT_EVIDENCE
from app.config import Settings
from app.incidents import Incident
from app.memory import InMemoryIncidentRepository, IncidentMemoryService
from app.memory.seed import seed_mastercard_d2

DECLINE_PROFILE = {"NO_DECLINE": 98, "PROVIDER_TIMEOUT": 96, "DO_NOT_HONOR": 46}


def _incident(**overrides) -> Incident:
    payload = {
        "schema_version": "1.0",
        "incident_id": "inc_agent_test_001",
        "state": "SUPPORTED",
        "detected_at": "2026-08-30T12:05:00Z",
        "estimated_started_at": "2026-08-30T12:00:00Z",
        "title": "Payment degradation for country=BR, provider_id=dlocal",
        "scope": {"country": ["BR"], "provider_id": ["dlocal"]},
        "metrics": {
            "eligible_attempts": 240,
            "approval_rate_observed": 0.41,
            "approval_rate_expected": 0.87,
            "lost_approvals": 110,
        },
        "root_cause": {
            "status": "SUPPORTED",
            "category": "PROVIDER_DEGRADATION",
            "confidence": 0.82,
            "confidence_factors": {"contribution": 0.9},
            "alternatives": [{"category": "COUNTRY_LOCALIZED_DEGRADATION", "confidence": 0.51}],
        },
        "impact": {
            "metric": "GMV_AT_RISK",
            "amount_minor": 4820000,
            "currency": "BRL",
            "method": "EXPECTED_APPROVAL_SHORTFALL",
        },
        "evidence": [
            {
                "evidence_id": "evd_det_one",
                "kind": "DETECTOR_CANDIDATE",
                "statement": "Detector candidate cand_one contributed to this Incident.",
                "source_ref": "window://2026-08-30T12:00:00Z/provider_id=dlocal",
            },
            {
                "evidence_id": "evd_decline_one",
                "kind": "DECLINE_PROFILE",
                "statement": "Dominant decline profile is PROVIDER_TIMEOUT across 96 eligible attempts in this slice.",
                "source_ref": "window://decline-profile",
            },
        ],
        "recommendations": [],
        "limitations": [],
        "correlation_id": "corr_agent_test_001",
    }
    payload.update(overrides)
    return Incident.model_validate(payload)


class FakeClient:
    """Return a fixed body, so a test can describe exactly what a model 'said'."""

    def __init__(self, body: str, *, model_version: str = "fake-model-v1") -> None:
        self.body = body
        self.model_version = model_version
        self.calls = 0

    def suggest(self, pack, trace) -> str:
        self.calls += 1
        return self.body


class ExplodingClient:
    model_version = "exploding-v1"

    def suggest(self, pack, trace) -> str:
        raise RuntimeError("model endpoint unreachable")


def _valid_body(**overrides) -> str:
    payload = {
        "schema_version": "1.0",
        "incident_id": "inc_agent_test_001",
        "evidence_fingerprint": "overwritten-by-the-service",
        "status": "SUGGESTED",
        "suggested_category": "PROVIDER_DEGRADATION",
        "summary_for_operations": "Provider dlocal in BR is likely degraded; investigate before concluding.",
        "executive_summary": "About 48,200.00 BRL of GMV is at risk in BR.",
        "reasons": [{"statement": "Detector isolated the provider slice.", "evidence_ids": ["evd_det_one"]}],
        "confidence": 0.6,
        "recommended_actions": [
            {
                "action": "Verify the provider status page and compare with the baseline window.",
                "execution": "HUMAN_ONLY",
                "rationale_evidence_ids": ["evd_det_one"],
            }
        ],
        "limitations": [],
        "retrieval_trace": {},
        "model_version": "fake-model-v1",
    }
    payload.update(overrides)
    return json.dumps(payload)


def _service(client, **kwargs) -> DiagnosticAgentService:
    return DiagnosticAgentService(client=client, **kwargs)


def test_configured_client_uses_template_without_an_api_key():
    client = configured_suggestion_client(Settings(_env_file=None, openai_api_key=None))

    assert isinstance(client, TemplateSuggestionClient)


def test_configured_openai_client_uses_terra_high_responses_request(monkeypatch):
    calls = {}

    class FakeResponses:
        def create(self, **kwargs):
            calls["request"] = kwargs
            return types.SimpleNamespace(output_text='{"status":"SUGGESTED"}')

    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls["initialization"] = kwargs
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=FakeOpenAI))
    client = configured_suggestion_client(
        Settings(
            _env_file=None,
            openai_api_key="test-key",
            openai_model="gpt-5.6-terra",
            openai_reasoning_effort="high",
            openai_timeout_seconds=9,
        )
    )
    assert isinstance(client, OpenAISuggestionClient)

    pack = build_evidence_pack(_incident(), decline_profile=DECLINE_PROFILE)
    trace = AgentRetrievalTrace(
        incident_id=pack.incident_id,
        status="NO_PRECEDENT",
        filter_criteria="same scope",
        candidate_count=0,
        index_version="local-v1",
    )
    assert client.suggest(pack, trace) == '{"status":"SUGGESTED"}'
    assert calls["initialization"] == {"api_key": "test-key", "timeout": 9, "max_retries": 0}
    assert calls["request"]["model"] == "gpt-5.6-terra"
    assert calls["request"]["reasoning"] == {"effort": "high"}
    assert calls["request"]["store"] is False
    assert calls["request"]["text"] == {"format": {"type": "json_object"}}
    assert "JSON" in calls["request"]["input"]
    assert "Do not mention, quote or reuse engine status labels" in system_prompt()


def test_new_incident_without_precedent_is_suggested_from_current_evidence():
    """NO_PRECEDENT must not end the investigation (DEC-026)."""
    client = FakeClient(_valid_body())
    suggestion = _service(client).suggest_for_incident(_incident(), decline_profile=DECLINE_PROFILE)

    assert suggestion.status == "SUGGESTED"
    assert suggestion.retrieval_trace["status"] == "NO_PRECEDENT"
    assert suggestion.suggested_category == "PROVIDER_DEGRADATION"
    assert [reason.evidence_ids for reason in suggestion.reasons] == [["evd_det_one"]]


def test_no_precedent_does_not_become_inconclusive_or_change_root_cause():
    incident = _incident()
    suggestion = _service(FakeClient(_valid_body())).suggest_for_incident(
        incident, decline_profile=DECLINE_PROFILE
    )

    assert suggestion.status not in {"INCONCLUSIVE", "SUPPORTED"}
    assert suggestion.retrieval_trace["status"] == "NO_PRECEDENT"
    # The engine's diagnosis is untouched by anything the agent produced.
    assert incident.root_cause.status == "SUPPORTED"
    assert incident.root_cause.category == "PROVIDER_DEGRADATION"


def test_single_evidence_source_yields_insufficient_evidence():
    """OPEN-AGT-003 fallback: one source is not two independent observations."""
    incident = _incident(
        evidence=[
            {
                "evidence_id": "evd_only_one",
                "kind": "DETECTOR_CANDIDATE",
                "statement": "Detector candidate cand_solo contributed to this Incident.",
                "source_ref": "window://single-source",
            }
        ]
    )
    client = FakeClient(_valid_body())
    suggestion = _service(client).suggest_for_incident(incident, decline_profile=DECLINE_PROFILE)

    assert suggestion.status == "INSUFFICIENT_EVIDENCE"
    assert suggestion.suggested_category is None
    assert suggestion.confidence == 0.0
    assert suggestion.recommended_actions == []
    assert client.calls == 0, "the client must not be asked to guess below the evidence floor"
    assert any(str(MINIMUM_INDEPENDENT_EVIDENCE) in item for item in suggestion.limitations)


def test_memory_unavailable_keeps_the_suggestion_and_states_the_limitation():
    class BrokenMemory:
        def retrieve(self, incident):
            raise ConnectionError("neo4j is down")

    suggestion = _service(
        FakeClient(_valid_body()), memory_service=BrokenMemory()
    ).suggest_for_incident(_incident(), decline_profile=DECLINE_PROFILE)

    assert suggestion.status == "SUGGESTED"
    assert suggestion.retrieval_trace["status"] == "MEMORY_UNAVAILABLE"
    assert any("memory was unavailable" in item.lower() for item in suggestion.limitations)


def test_incident_survives_when_the_client_raises():
    suggestion = _service(ExplodingClient()).suggest_for_incident(
        _incident(), decline_profile=DECLINE_PROFILE
    )

    assert suggestion.status == "UNAVAILABLE"
    assert suggestion.suggested_category is None
    assert any("RuntimeError" in item for item in suggestion.limitations)


def test_malformed_model_response_is_rejected_as_unavailable():
    suggestion = _service(FakeClient("here is my analysis: the provider is down")).suggest_for_incident(
        _incident(), decline_profile=DECLINE_PROFILE
    )

    assert suggestion.status == "UNAVAILABLE"
    assert any("not valid JSON" in item for item in suggestion.limitations)


def test_invented_evidence_id_is_rejected():
    body = _valid_body(
        reasons=[{"statement": "A precedent from last Tuesday matches.", "evidence_ids": ["evd_invented_999"]}]
    )
    suggestion = _service(FakeClient(body)).suggest_for_incident(_incident(), decline_profile=DECLINE_PROFILE)

    assert suggestion.status == "UNAVAILABLE"
    assert any("evd_invented_999" in item for item in suggestion.limitations)


def test_non_human_only_execution_is_rejected():
    body = _valid_body(
        recommended_actions=[
            {
                "action": "Verify the provider status page.",
                "execution": "AUTOMATIC",
                "rationale_evidence_ids": ["evd_det_one"],
            }
        ]
    )
    suggestion = _service(FakeClient(body)).suggest_for_incident(_incident(), decline_profile=DECLINE_PROFILE)

    assert suggestion.status == "UNAVAILABLE"
    assert suggestion.recommended_actions == []


@pytest.mark.parametrize(
    "action",
    [
        "Retry the declined attempts through the backup provider.",
        "Reroute BR card traffic to adyen immediately.",
        "Refund the affected customers.",
        "Capture the pending authorizations before they expire.",
    ],
)
def test_payment_execution_actions_are_rejected(action):
    body = _valid_body(
        recommended_actions=[
            {"action": action, "execution": "HUMAN_ONLY", "rationale_evidence_ids": ["evd_det_one"]}
        ]
    )
    suggestion = _service(FakeClient(body)).suggest_for_incident(_incident(), decline_profile=DECLINE_PROFILE)

    assert suggestion.status == "UNAVAILABLE"
    assert any("investigation steps" in item for item in suggestion.limitations)


def test_attempt_to_write_root_cause_is_rejected():
    payload = json.loads(_valid_body())
    payload["root_cause"] = {"status": "SUPPORTED", "category": "FRAUD", "confidence": 0.99}
    suggestion = _service(FakeClient(json.dumps(payload))).suggest_for_incident(
        _incident(), decline_profile=DECLINE_PROFILE
    )

    assert suggestion.status == "UNAVAILABLE"
    assert any("engine-owned fields" in item for item in suggestion.limitations)


def test_attempt_to_promote_status_to_supported_is_rejected():
    suggestion = _service(FakeClient(_valid_body(status="SUPPORTED"))).suggest_for_incident(
        _incident(), decline_profile=DECLINE_PROFILE
    )

    assert suggestion.status == "UNAVAILABLE"
    assert any("causal status" in item for item in suggestion.limitations)


def test_confirmatory_fraud_language_is_rejected():
    body = _valid_body(
        summary_for_operations="The declines prove this is fraud on the BR card traffic.",
        limitations=["SUSPECTED_FRAUD noted."],
    )
    suggestion = _service(FakeClient(body)).suggest_for_incident(
        _incident(), decline_profile={"SUSPECTED_FRAUD": 80, "NO_DECLINE": 20}
    )

    assert suggestion.status == "UNAVAILABLE"
    assert any("fraud as established fact" in item for item in suggestion.limitations)


def test_suspected_fraud_declines_produce_a_hypothesis_with_an_explicit_caveat():
    """A SUSPECTED_FRAUD decline profile must not become a fraud verdict."""
    body = _valid_body(
        suggested_category="POSSIBLE_RISK_CONTROL_BLOCK",
        summary_for_operations="Declines concentrate on risk-control responses; investigate the rule set.",
    )
    suggestion = _service(FakeClient(body)).suggest_for_incident(
        _incident(), decline_profile={"SUSPECTED_FRAUD": 80, "NO_DECLINE": 20}
    )

    assert suggestion.status == "SUGGESTED"
    assert suggestion.suggested_category == "POSSIBLE_RISK_CONTROL_BLOCK"
    assert any("SUSPECTED_FRAUD" in item and "not proof of fraud" in item for item in suggestion.limitations)


def test_reprocessing_the_same_incident_is_idempotent():
    incident = _incident()
    client = FakeClient(_valid_body())
    service = _service(client)

    first = service.suggest_for_incident(incident, decline_profile=DECLINE_PROFILE)
    second = service.suggest_for_incident(incident, decline_profile=DECLINE_PROFILE)

    assert first == second
    assert client.calls == 1, "an unchanged Incident must not pay for a second model call"
    assert DiagnosticSuggestionRepository().count_for_incident(incident.incident_id) == 1


def test_changed_evidence_produces_a_new_suggestion_record():
    """A different fingerprint is a different fact set, so it earns its own record."""
    service = _service(FakeClient(_valid_body()))
    service.suggest_for_incident(_incident(), decline_profile=DECLINE_PROFILE)
    service.suggest_for_incident(_incident(), decline_profile={"PROVIDER_TIMEOUT": 200})

    assert DiagnosticSuggestionRepository().count_for_incident("inc_agent_test_001") == 2


def test_template_client_needs_no_api_key():
    suggestion = DiagnosticAgentService(client=TemplateSuggestionClient()).suggest_for_incident(
        _incident(), decline_profile=DECLINE_PROFILE, persist=False
    )

    assert suggestion.model_version == TemplateSuggestionClient.model_version
    assert suggestion.status == "SUGGESTED"
    assert all(action.execution == "HUMAN_ONLY" for action in suggestion.recommended_actions)


def test_matched_precedent_is_cited_without_becoming_the_current_cause():
    fallback = InMemoryIncidentRepository()
    seed_mastercard_d2(fallback)
    memory = IncidentMemoryService(fallback, threshold=0.0)
    incident = _incident(
        scope={"provider_id": ["mastercard_gateway"], "country": ["BR"]},
        root_cause={
            "status": "INCONCLUSIVE",
            "category": None,
            "confidence": 0.4,
            "confidence_factors": {"contribution": 0.4},
            "alternatives": [],
        },
        state="INCONCLUSIVE",
    )
    suggestion = DiagnosticAgentService(
        client=TemplateSuggestionClient(), memory_service=memory
    ).suggest_for_incident(incident, decline_profile=DECLINE_PROFILE, persist=False)

    assert suggestion.status in {"SUGGESTED", "INSUFFICIENT_EVIDENCE"}
    assert any(
        "INCONCLUSIVE" in item and "does not change it" in item for item in suggestion.limitations
    )


def test_evidence_pack_exposes_only_persisted_facts():
    pack = build_evidence_pack(_incident(), decline_profile=DECLINE_PROFILE)

    assert pack.authorized_evidence_ids == ["evd_decline_one", "evd_det_one"]
    assert pack.root_cause.status == "SUPPORTED"
    assert pack.evidence_fingerprint
    assert pack.independent_evidence_count == 2
    # The pack is a value object: it carries no connection, cursor or credential.
    assert set(pack.model_dump()) == {
        "schema_version",
        "incident_id",
        "correlation_id",
        "evidence_fingerprint",
        "scope",
        "window",
        "approval_rate_observed",
        "approval_rate_expected",
        "eligible_attempts",
        "lost_approvals",
        "impact",
        "detector_evidence",
        "rca_alternatives",
        "decline_profile",
        "refusal_code_summaries",
        "limitations",
        "authorized_evidence_ids",
        "root_cause",
        "engine_version",
    }


def test_missing_decline_profile_is_declared_as_a_limitation():
    pack = build_evidence_pack(_incident(), decline_profile=None)

    assert pack.decline_profile == {}
    assert any("decline profile" in item for item in pack.limitations)
