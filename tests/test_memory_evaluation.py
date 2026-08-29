"""Development evaluation set for CTR-MEM-001 baseline behavior.

These cases are intentionally separate from unit-level implementation tests: they
name the product outcomes that must survive future reranking and Neo4j wiring.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import unittest

from app.memory import IncidentMemoryService, InMemoryIncidentRepository, MemoryStatus
from app.memory.seed import mastercard_d2_precedent, seed_mastercard_d2
from tests.test_memory_service import current_incident


class MemoryBaselineEvaluation(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryIncidentRepository()
        seed_mastercard_d2(self.repository, now=datetime(2026, 8, 29, tzinfo=timezone.utc))

    def test_eval_mem_001_exact_mastercard_recurrence_is_top_1(self) -> None:
        result = IncidentMemoryService(self.repository).retrieve(current_incident())

        self.assertEqual(MemoryStatus.MATCH_FOUND, result.memory_status)
        self.assertEqual("INC-HIST-002D-MASTERCARD", result.matches[0].incident_id)
        self.assertGreaterEqual(result.matches[0].structured_score, 0.8)

    def test_eval_mem_002_new_combination_returns_no_precedent(self) -> None:
        result = IncidentMemoryService(self.repository).retrieve(current_incident(brand="VISA"))

        self.assertEqual(MemoryStatus.NO_PRECEDENT, result.memory_status)
        self.assertEqual((), result.matches)

    def test_eval_mem_003_inconclusive_still_returns_historical_context(self) -> None:
        incident = current_incident(status="INCONCLUSIVE")
        result = IncidentMemoryService(self.repository).retrieve(incident)

        self.assertEqual(MemoryStatus.MATCH_FOUND, result.memory_status)
        self.assertEqual("INCONCLUSIVE", incident.root_cause_status)

    def test_eval_mem_004_unconfirmed_history_is_not_authoritative(self) -> None:
        repository = InMemoryIncidentRepository()
        precedent = mastercard_d2_precedent(now=datetime(2026, 8, 29, tzinfo=timezone.utc))
        repository.upsert(replace(precedent, confirmation="UNCONFIRMED"))

        result = IncidentMemoryService(repository).retrieve(current_incident())

        self.assertEqual(MemoryStatus.NO_PRECEDENT, result.memory_status)

    def test_eval_mem_005_memory_failure_is_distinct_from_no_precedent(self) -> None:
        result = IncidentMemoryService(InMemoryIncidentRepository(available=False)).retrieve(current_incident())

        self.assertEqual(MemoryStatus.MEMORY_UNAVAILABLE, result.memory_status)
        self.assertEqual((), result.matches)


if __name__ == "__main__":
    unittest.main()

