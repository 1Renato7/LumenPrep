from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.explanation import GroundedExplainer, Playbook, validate_evidence_ids
from app.memory import IncidentMemoryService, InMemoryIncidentRepository
from app.memory.seed import seed_mastercard_d2
from tests.test_memory_service import current_incident


class GroundedExplainerTest(unittest.TestCase):
    def setUp(self) -> None:
        repository = InMemoryIncidentRepository()
        seed_mastercard_d2(repository, now=datetime(2026, 8, 29, tzinfo=timezone.utc))
        self.memory = IncidentMemoryService(repository).retrieve(current_incident())
        self.explainer = GroundedExplainer(
            [
                Playbook(
                    playbook_id="PB-GENERIC-INVESTIGATION",
                    cause_categories=frozenset(),
                    required_scope={},
                    action="Inspect current evidence and escalate to the payment operations owner.",
                    cautions=("Do not execute payment actions automatically.",),
                ),
                Playbook(
                    playbook_id="PB-ISSUER-INVESTIGATION",
                    cause_categories=frozenset({"ISSUER_OUTAGE"}),
                    required_scope={"card_brand": frozenset({"MASTERCARD"})},
                    action="Ask the issuer/provider operations team to investigate the observed decline pattern.",
                    cautions=("Confirm the current scope before reusing a historical procedure.",),
                ),
            ]
        )

    def test_template_is_grounded_and_human_only(self) -> None:
        bundle = self.explainer.explain(current_incident(), self.memory)
        contract = bundle.to_contract()

        self.assertEqual(contract["execution"], "HUMAN_ONLY")
        self.assertEqual(contract["playbook_id"], "PB-ISSUER-INVESTIGATION")
        self.assertIn("EVID-CURRENT-001", contract["evidence_ids"])
        self.assertIn("EVID-HIST-MC-001", contract["evidence_ids"])
        validate_evidence_ids(bundle, current_incident(), self.memory)

    def test_inconclusive_incident_does_not_prioritize_historical_playbook(self) -> None:
        incident = current_incident(status="INCONCLUSIVE")
        bundle = self.explainer.explain(incident, self.memory)

        self.assertEqual(bundle.playbook_id, "PB-GENERIC-INVESTIGATION")
        self.assertTrue(any("INCONCLUSIVE" in item for item in bundle.limitations))

    def test_unknown_evidence_id_is_rejected(self) -> None:
        bundle = self.explainer.explain(current_incident(), self.memory)
        invalid = bundle.__class__(
            **{**bundle.__dict__, "evidence_ids": ("EVID-UNKNOWN",)}
        )

        with self.assertRaises(ValueError):
            validate_evidence_ids(invalid, current_incident(), self.memory)

    def test_supported_without_evidence_does_not_publish_causal_claim(self) -> None:
        payload = {
            "incident_id": "INC-WITHOUT-EVIDENCE",
            "detected_at": "2026-08-29T15:00:00Z",
            "scope": {"provider": ["stripe"], "country": ["BR"], "card_brand": ["MASTERCARD"]},
            "metrics": {"decline_codes": ["DO_NOT_HONOR"], "temporal_shape": "sudden_approval_drop"},
            "root_cause": {"status": "SUPPORTED", "category": "ISSUER_OUTAGE"},
            "evidence": [],
            "correlation_id": "corr-no-evidence",
        }
        from app.memory import IncidentMemoryService
        from app.memory.models import Incident

        incident = Incident.from_contract(payload)
        bundle = self.explainer.explain(incident, self.memory)

        self.assertEqual(bundle.playbook_id, "PB-GENERIC-INVESTIGATION")
        self.assertIsNone(bundle.recurrence_statement)
        self.assertIn("withheld", bundle.where_and_why)


if __name__ == "__main__":
    unittest.main()

