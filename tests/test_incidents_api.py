from __future__ import annotations

import unittest
from unittest.mock import patch

from app.api import incidents
from app.memory import Neo4jIncidentRepository


class MemoryRepositorySelectionTest(unittest.TestCase):
    def setUp(self) -> None:
        incidents._neo4j_driver = None
        incidents._neo4j_driver_failed = False

    def tearDown(self) -> None:
        incidents._neo4j_driver = None
        incidents._neo4j_driver_failed = False

    def test_uses_in_memory_only_when_neo4j_not_configured(self) -> None:
        with patch.object(incidents.settings, "neo4j_uri", None):
            primary = incidents._memory_repository()
        self.assertIsNone(primary)

    def test_uses_neo4j_when_configured_and_driver_builds(self) -> None:
        fake_driver = object()
        with (
            patch.object(incidents.settings, "neo4j_uri", "bolt://localhost:7687"),
            patch.object(incidents.settings, "neo4j_user", "neo4j"),
            patch.object(incidents.settings, "neo4j_password", "secret"),
            patch.object(incidents, "_neo4j_driver_instance", return_value=fake_driver),
        ):
            primary = incidents._memory_repository()
        self.assertIsInstance(primary, Neo4jIncidentRepository)
        self.assertIs(primary.driver, fake_driver)

    def test_falls_back_to_in_memory_when_driver_construction_fails(self) -> None:
        with (
            patch.object(incidents.settings, "neo4j_uri", "bolt://localhost:7687"),
            patch.object(incidents, "_neo4j_driver_instance", return_value=None),
        ):
            primary = incidents._memory_repository()
        self.assertIsNone(primary)

    def test_get_incident_still_serves_real_enrichment_ids_without_neo4j(self) -> None:
        with patch.object(incidents.settings, "neo4j_uri", None):
            response = incidents.get_incident("inc_current_mastercard_001")
        self.assertEqual(response["incident"]["incident_id"], "inc_current_mastercard_001")
        self.assertIn(response["memory"]["memory_status"], {"MATCH_FOUND", "NO_PRECEDENT"})


if __name__ == "__main__":
    unittest.main()
