"""Tests for optional OpenAI Structured Outputs integration."""

from __future__ import annotations

import json
import unittest

from app.explanation import GroundedExplainer, OpenAIResponsesExplainer
from app.memory.models import Incident, MemoryStatus, RetrievalTrace, SimilarIncidentResult


class _Response:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class _Responses:
    def __init__(self, output_text: str | None = None, error: Exception | None = None) -> None:
        self.output_text = output_text
        self.error = error
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> _Response:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return _Response(self.output_text or "{}")


class _Client:
    def __init__(self, responses: _Responses) -> None:
        self.responses = responses


class OpenAIResponsesExplainerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.incident = Incident.from_contract(
            {
                "incident_id": "inc-current",
                "detected_at": "2026-08-29T12:00:00Z",
                "scope": {"provider": "mastercard", "country": "BR"},
                "metrics": {"decline_rate": 0.31},
                "root_cause": {"status": "SUPPORTED", "category": "PROVIDER_OUTAGE"},
                "evidence": [{"evidence_id": "ev-current"}],
                "correlation_id": "corr-current",
            }
        )
        self.memory = SimilarIncidentResult(
            query_incident_id=self.incident.incident_id,
            memory_status=MemoryStatus.NO_PRECEDENT,
            matches=(),
            retrieval_trace=RetrievalTrace("baseline", 0, None, "v1", False),
            correlation_id=self.incident.correlation_id,
        )
        self.fallback = GroundedExplainer([])

    def test_calls_strict_structured_outputs_and_accepts_grounded_bundle(self) -> None:
        expected = self.fallback.explain(self.incident, self.memory).to_contract()
        expected["model_version"] = "gpt-5.6-terra"
        expected["claim_evidence"] = {
            "executive_summary": ["ev-current"],
            "operations_summary": ["ev-current"],
            "what_happened": ["ev-current"],
            "where_and_why": ["ev-current"],
            "recurrence_statement": [],
        }
        responses = _Responses(json.dumps(expected))
        explainer = OpenAIResponsesExplainer(self.fallback, _Client(responses))

        bundle = explainer.explain(self.incident, self.memory)

        self.assertEqual("gpt-5.6-terra", bundle.model_version)
        call = responses.calls[0]
        self.assertEqual("gpt-5.6-terra", call["model"])
        self.assertFalse(call["store"])
        self.assertTrue(call["text"]["format"]["strict"])
        self.assertEqual("json_schema", call["text"]["format"]["type"])

    def test_uses_deterministic_fallback_when_api_fails(self) -> None:
        explainer = OpenAIResponsesExplainer(self.fallback, _Client(_Responses(error=RuntimeError("down"))))

        bundle = explainer.explain(self.incident, self.memory)

        self.assertEqual("deterministic-template", bundle.model_version)

    def test_inconclusive_or_evidenceless_incidents_do_not_call_the_model(self) -> None:
        responses = _Responses("should not be used")
        inconclusive = Incident.from_contract(
            {
                "incident_id": "inc-inconclusive",
                "detected_at": "2026-08-29T12:00:00Z",
                "scope": {"provider": "mastercard"},
                "metrics": {},
                "root_cause": {"status": "INCONCLUSIVE", "category": None},
                "evidence": [],
                "correlation_id": "corr-inconclusive",
            }
        )
        explainer = OpenAIResponsesExplainer(self.fallback, _Client(responses))

        bundle = explainer.explain(inconclusive, self.memory)

        self.assertEqual("deterministic-template", bundle.model_version)
        self.assertEqual([], responses.calls)

    def test_rejects_unknown_evidence_from_model_and_falls_back(self) -> None:
        unsafe = self.fallback.explain(self.incident, self.memory).to_contract()
        unsafe["evidence_ids"] = ["untrusted-evidence"]
        unsafe["claim_evidence"] = {
            "executive_summary": ["ev-current"],
            "operations_summary": ["ev-current"],
            "what_happened": ["ev-current"],
            "where_and_why": ["ev-current"],
            "recurrence_statement": [],
        }
        explainer = OpenAIResponsesExplainer(self.fallback, _Client(_Responses(json.dumps(unsafe))))

        bundle = explainer.explain(self.incident, self.memory)

        self.assertEqual(("ev-current",), bundle.evidence_ids)
        self.assertEqual("deterministic-template", bundle.model_version)

    def test_rejects_generated_claim_without_current_evidence_citation(self) -> None:
        unsafe = self.fallback.explain(self.incident, self.memory).to_contract()
        unsafe["model_version"] = "gpt-5.6-terra"
        unsafe["claim_evidence"] = {
            "executive_summary": [],
            "operations_summary": ["ev-current"],
            "what_happened": ["ev-current"],
            "where_and_why": ["ev-current"],
            "recurrence_statement": [],
        }
        explainer = OpenAIResponsesExplainer(self.fallback, _Client(_Responses(json.dumps(unsafe))))

        bundle = explainer.explain(self.incident, self.memory)

        self.assertEqual("deterministic-template", bundle.model_version)


if __name__ == "__main__":
    unittest.main()

