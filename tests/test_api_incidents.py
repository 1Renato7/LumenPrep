from __future__ import annotations

import unittest
from unittest.mock import patch

from app.api.incidents import _fixture_records, _memory_and_explanation
from app.memory import Incident, IncidentMemoryService, InMemoryIncidentRepository
from app.memory.seed import seed_mastercard_d2


class _RuntimeStub:
    def __init__(self, service: IncidentMemoryService) -> None:
        self.service = service
        self.closed = False

    def close(self) -> None:
        self.closed = True


class IncidentApiMemoryRuntimeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = _fixture_records()["inc_current_mastercard_001"]

    def test_unconfigured_graph_uses_explicit_seeded_fallback(self) -> None:
        with patch("app.api.incidents.create_memory_runtime", side_effect=RuntimeError("missing Neo4j config")):
            memory, explanation = _memory_and_explanation(self.payload)

        self.assertEqual("MATCH_FOUND", memory["memory_status"])
        self.assertTrue(memory["retrieval_trace"]["fallback_used"])
        self.assertEqual("INC-HIST-002D-MASTERCARD", memory["matches"][0]["incident_id"])
        self.assertEqual(self.payload["incident_id"], explanation["incident_id"])

    def test_configured_runtime_is_used_and_closed(self) -> None:
        incident = Incident.from_contract(self.payload)
        repository = InMemoryIncidentRepository()
        seed_mastercard_d2(repository, now=incident.detected_at)
        runtime = _RuntimeStub(IncidentMemoryService(repository))

        with patch("app.api.incidents.create_memory_runtime", return_value=runtime) as create_runtime:
            memory, _ = _memory_and_explanation(self.payload)

        create_runtime.assert_called_once_with()
        self.assertTrue(runtime.closed)
        self.assertFalse(memory["retrieval_trace"]["fallback_used"])
        self.assertEqual("MATCH_FOUND", memory["memory_status"])


if __name__ == "__main__":
    unittest.main()
