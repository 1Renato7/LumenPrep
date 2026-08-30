import json
from pathlib import Path

from app.agent import DiagnosticAgentService, DiagnosticSuggestionRepository
from app.agent.llm import TemplateSuggestionClient
from app.incidents import Incident


FIXTURE_PATH = Path("contracts/fixtures/incident-mastercard-recurrence.json")


def _incident() -> Incident:
    return Incident.model_validate(json.loads(FIXTURE_PATH.read_text(encoding="utf-8")))


def test_template_suggestion_is_grounded_human_only_and_does_not_change_the_incident():
    incident = _incident()
    original_root_cause = incident.root_cause.model_dump(mode="json")

    suggestion = DiagnosticAgentService(client=TemplateSuggestionClient()).suggest_for_incident(
        incident, persist=False
    )

    assert suggestion.status == "SUGGESTED"
    assert suggestion.suggested_category == incident.root_cause.category
    assert suggestion.reasons
    assert all(action.execution == "HUMAN_ONLY" for action in suggestion.recommended_actions)
    assert incident.root_cause.model_dump(mode="json") == original_root_cause


def test_template_uses_concise_operational_portuguese():
    suggestion = DiagnosticAgentService(client=TemplateSuggestionClient()).suggest_for_incident(
        _incident(), decline_profile={"NO_DECLINE": 98, "PROVIDER_TIMEOUT": 96}, persist=False
    )

    assert "Prioridade:" in suggestion.summary_for_operations
    assert "PROVIDER_TIMEOUT" in suggestion.summary_for_operations
    assert "Ação humana prioritária:" in suggestion.executive_summary
    assert len(suggestion.recommended_actions) <= 2
    assert "latência do provedor" in suggestion.recommended_actions[0].action


def test_agent_rejects_a_model_action_that_would_reroute_payment_traffic():
    class UnsafeClient:
        model_version = "unsafe-test-v1"

        def suggest(self, pack, trace) -> str:
            payload = json.loads(TemplateSuggestionClient().suggest(pack, trace))
            payload["recommended_actions"][0]["action"] = "Reroute payment traffic immediately."
            return json.dumps(payload)

    suggestion = DiagnosticAgentService(client=UnsafeClient()).suggest_for_incident(_incident(), persist=False)

    assert suggestion.status == "UNAVAILABLE"
    assert suggestion.suggested_category is None
    assert suggestion.recommended_actions == []


def test_unchanged_incident_reuses_one_persisted_suggestion():
    incident = _incident()
    service = DiagnosticAgentService(client=TemplateSuggestionClient())

    first = service.suggest_for_incident(incident)
    second = service.suggest_for_incident(incident)

    repository = DiagnosticSuggestionRepository()
    assert first.evidence_fingerprint == second.evidence_fingerprint
    assert repository.count_for_incident(incident.incident_id) == 1
