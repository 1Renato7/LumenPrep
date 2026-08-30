import pytest
from fastapi.testclient import TestClient

from app.evaluation.case_evaluator import CaseEvaluator, ProbeResult, _output_text
from app.config import settings
from app.evaluation import InProcessApi
from main import create_app


class _Planner:
    model = "test-model"

    def choose_operations(self, *, case_context: str, focus: str) -> list[str]:
        assert focus == "idempotency"
        return ["health", "idempotency", "invalid_input"]

    def write_feedback(self, *, case_context: str, focus: str, probes: list[ProbeResult]) -> str:
        assert len(probes) == 3
        return "PRONTA COM LIMITAÇÕES: feedback simulated."


class _Api:
    def __init__(self) -> None:
        self.submissions = 0

    def request(self, method: str, path: str, *, payload=None, headers=None):
        if path == "/v1/health":
            return 200, {"status": "ok"}
        if path == "/v1/transaction-batches":
            self.submissions += 1
            if payload["transactions"][0].get("status"):
                return 422, {"detail": "invalid"}
            if self.submissions == 3:
                return 409, {"detail": "IDEMPOTENCY_KEY_CONFLICT"}
            return 202, {"transaction_ids": ["txn-1"]}
        raise AssertionError(path)


def test_evaluator_runs_only_model_selected_allowlisted_probes_and_returns_feedback():
    report = CaseEvaluator(api=_Api(), planner=_Planner(), case_context="case requirements").run(focus="idempotency")

    assert report.passed is True
    assert [probe.name for probe in report.probes] == ["health", "idempotency", "invalid_input"]
    assert report.feedback.startswith("Veredito: PRONTA COM LIMITAÇÕES")


def test_failed_probe_forces_a_non_ready_verdict_even_when_the_planner_claims_ready():
    class _FailingApi(_Api):
        def request(self, method: str, path: str, *, payload=None, headers=None):
            if path == "/v1/health":
                return 503, {"status": "down"}
            return super().request(method, path, payload=payload, headers=headers)

    report = CaseEvaluator(api=_FailingApi(), planner=_Planner(), case_context="case requirements").run(focus="idempotency")

    assert report.passed is False
    assert report.feedback.startswith("Veredito: NÃO PRONTA")


def test_missing_openai_output_describes_the_response_state():
    with pytest.raises(RuntimeError, match="status=incomplete"):
        _output_text({"status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"}, "output": []})


def test_neo4j_probe_requires_complete_configuration(monkeypatch):
    monkeypatch.setattr(settings, "neo4j_uri", None)
    probe = CaseEvaluator(api=_Api(), planner=_Planner(), case_context="case requirements")._probe_neo4j()

    assert probe.passed is False
    assert probe.evidence == "Neo4j configuration is incomplete."


def test_provenance_probe_rebuilds_a_simulated_error_from_the_durable_events():
    with TestClient(create_app(settings)) as client:
        probe = CaseEvaluator(api=InProcessApi(client), planner=_Planner(), case_context="case requirements")._probe_error_provenance()

    assert probe.passed is True
    assert "status=FAILED" in probe.evidence


def test_transport_probe_detects_when_the_same_public_facts_change_in_serialization():
    with TestClient(create_app(settings)) as client:
        probe = CaseEvaluator(api=InProcessApi(client), planner=_Planner(), case_context="case requirements")._probe_transport_equivalence()

    assert probe.passed is True
    assert "Same public facts" in probe.evidence
