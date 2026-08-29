from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import datetime, timezone

from app.memory import HistoricalIncident, Incident, IncidentMemoryService, InMemoryIncidentRepository, MemoryStatus
from app.memory.seed import mastercard_d2_precedent, seed_mastercard_d2


def current_incident(*, status: str = "SUPPORTED", brand: str = "MASTERCARD") -> Incident:
    return Incident.from_contract(
        {
            "incident_id": "INC-CURRENT-001",
            "detected_at": "2026-08-29T15:00:00Z",
            "scope": {"provider": ["stripe"], "country": ["BR"], "card_brand": [brand]},
            "metrics": {
                "decline_codes": ["DO_NOT_HONOR", "ISSUER_UNAVAILABLE"],
                "temporal_shape": "sudden_approval_drop",
            },
            "root_cause": {"status": status, "category": "ISSUER_OUTAGE" if status == "SUPPORTED" else None},
            "evidence": [
                {
                    "evidence_id": "EVID-CURRENT-001",
                    "kind": "WINDOW_METRIC",
                    "statement": "Approval rate fell in the scoped window.",
                    "source_ref": "fixture://current-incident",
                }
            ],
            "correlation_id": "corr-001",
        }
    )


class IncidentMemoryServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryIncidentRepository()
        seed_mastercard_d2(self.repository, now=datetime(2026, 8, 29, tzinfo=timezone.utc))
        self.service = IncidentMemoryService(self.repository)

    def test_d2_mastercard_is_top_match_and_seed_is_idempotent(self) -> None:
        seed_mastercard_d2(self.repository, now=datetime(2026, 8, 29, tzinfo=timezone.utc))
        result = self.service.retrieve(current_incident())

        self.assertEqual(self.repository.incident_count, 1)
        self.assertEqual(result.memory_status, MemoryStatus.MATCH_FOUND)
        self.assertEqual(result.matches[0].incident_id, "INC-HIST-002D-MASTERCARD")
        self.assertEqual(result.matches[0].confirmation, "HUMAN_CONFIRMED")
        self.assertIn("scope.card_brand=MASTERCARD", result.matches[0].matching_factors)
        self.assertIn("different_factors", result.matches[0].to_contract())

    def test_no_precedent_preserves_current_root_cause(self) -> None:
        incident = current_incident(brand="VISA")
        result = self.service.retrieve(incident)

        self.assertEqual(result.memory_status, MemoryStatus.NO_PRECEDENT)
        self.assertEqual(result.matches, ())
        self.assertEqual(incident.root_cause_status, "SUPPORTED")
        self.assertEqual(incident.root_cause_category, "ISSUER_OUTAGE")

    def test_inconclusive_incident_still_queries_memory(self) -> None:
        incident = current_incident(status="INCONCLUSIVE")
        result = self.service.retrieve(incident)

        self.assertEqual(result.memory_status, MemoryStatus.MATCH_FOUND)
        self.assertEqual(incident.root_cause_status, "INCONCLUSIVE")

    def test_unavailable_memory_is_not_no_precedent(self) -> None:
        unavailable = InMemoryIncidentRepository(available=False)
        result = IncidentMemoryService(unavailable).retrieve(current_incident())

        self.assertEqual(result.memory_status, MemoryStatus.MEMORY_UNAVAILABLE)
        self.assertEqual(result.matches, ())

    def test_fallback_preserves_contract(self) -> None:
        primary = InMemoryIncidentRepository(available=False)
        result = IncidentMemoryService(primary, fallback=self.repository).retrieve(current_incident())

        self.assertEqual(result.memory_status, MemoryStatus.MATCH_FOUND)
        self.assertTrue(result.retrieval_trace.fallback_used)

    def test_query_failure_uses_healthy_fallback(self) -> None:
        class QueryBrokenRepository(InMemoryIncidentRepository):
            def confirmed_incidents(self, query=None):
                raise ValueError("Neo4j query timeout")

        result = IncidentMemoryService(QueryBrokenRepository(), fallback=self.repository).retrieve(current_incident())

        self.assertEqual(result.memory_status, MemoryStatus.MATCH_FOUND)
        self.assertTrue(result.retrieval_trace.fallback_used)
        self.assertEqual(result.to_contract()["schema_version"], "1.1")

    def test_unconfirmed_candidate_never_becomes_a_precedent(self) -> None:
        repository = InMemoryIncidentRepository()
        precedent = mastercard_d2_precedent(now=datetime(2026, 8, 29, tzinfo=timezone.utc))
        repository.upsert(replace(precedent, confirmation="UNCONFIRMED"))

        result = IncidentMemoryService(repository).retrieve(current_incident())

        self.assertEqual(result.memory_status, MemoryStatus.NO_PRECEDENT)

    def test_old_or_scope_incompatible_candidates_are_filtered_before_scoring(self) -> None:
        repository = InMemoryIncidentRepository()
        old = replace(
            mastercard_d2_precedent(now=datetime(2026, 8, 29, tzinfo=timezone.utc)),
            occurred_at=datetime(2026, 7, 1, tzinfo=timezone.utc),
        )
        repository.upsert(old)

        result = IncidentMemoryService(repository).retrieve(current_incident())

        self.assertEqual(result.memory_status, MemoryStatus.NO_PRECEDENT)
        self.assertEqual(result.retrieval_trace.candidate_count, 0)

    def test_ties_have_stable_recency_then_id_order(self) -> None:
        repository = InMemoryIncidentRepository()
        seed = mastercard_d2_precedent(now=datetime(2026, 8, 29, tzinfo=timezone.utc))
        repository.upsert(replace(seed, incident_id="INC-Z"))
        repository.upsert(replace(seed, incident_id="INC-A"))

        result = IncidentMemoryService(repository).retrieve(current_incident())

        self.assertEqual(result.matches[0].incident_id, "INC-A")

    def test_current_incident_is_never_its_own_precedent(self) -> None:
        repository = InMemoryIncidentRepository()
        incident = current_incident()
        repository.upsert(
            HistoricalIncident(
                incident_id=incident.incident_id,
                occurred_at=incident.detected_at,
                scope=incident.scope,
                metrics=incident.metrics,
                confirmation="HUMAN_CONFIRMED",
                confirmed_cause="ISSUER_OUTAGE",
                prior_playbook_id="PB-ISSUER-INVESTIGATION",
                evidence_ids=("EVID-SELF",),
            )
        )

        result = IncidentMemoryService(repository).retrieve(incident)

        self.assertEqual(result.memory_status, MemoryStatus.NO_PRECEDENT)


if __name__ == "__main__":
    unittest.main()

