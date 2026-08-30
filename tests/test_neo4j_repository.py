from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.memory.neo4j_repository import Neo4jIncidentRepository
from app.memory.seed import mastercard_d2_precedent
from tests.test_memory_service import current_incident


class FakeResult:
    def __init__(self, rows=()):
        self.rows = rows

    def single(self):
        return {"healthy": 1}

    def __iter__(self):
        return iter(self.rows)

    def consume(self):
        return None


class FakeRecord(dict):
    def data(self):
        return dict(self)


class FakeSession:
    def __init__(self, rows=()):
        self.rows = rows
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def run(self, query, **parameters):
        self.calls.append((query, parameters))
        return FakeResult(self.rows)

    def execute_write(self, callback):
        return callback(self)


class FakeDriver:
    def __init__(self, rows=()):
        self.session_instance = FakeSession(rows)

    def session(self, **kwargs):
        return self.session_instance


class Neo4jIncidentRepositoryTest(unittest.TestCase):
    def test_health_upsert_and_query_use_scoped_deterministic_cypher(self) -> None:
        driver = FakeDriver()
        repository = Neo4jIncidentRepository(driver)

        self.assertTrue(repository.health())
        repository.upsert(mastercard_d2_precedent(now=datetime(2026, 8, 29, tzinfo=timezone.utc)))
        list(repository.confirmed_incidents(current_incident()))

        queries = [call[0] for call in driver.session_instance.calls]
        self.assertTrue(any("MERGE (incident:Incident" in query for query in queries))
        self.assertTrue(any("HUMAN_CONFIRMED" in query and "ORDER BY" in query for query in queries))
        upsert_parameters = next(parameters for query, parameters in driver.session_instance.calls if "MERGE (incident:Incident" in query)
        self.assertEqual(upsert_parameters["timeout"], 2.0)

    def test_upsert_reads_provider_id_into_providers_cypher_param(self) -> None:
        """scope.provider_id (contrato) -> $providers (Cypher) -> (:Provider {provider_id: ...}).
        Regressao: o adapter lia scope["provider"] (chave errada) e nunca criava o node Provider."""
        driver = FakeDriver()
        repository = Neo4jIncidentRepository(driver)

        repository.upsert(mastercard_d2_precedent(now=datetime(2026, 8, 29, tzinfo=timezone.utc)))

        query, parameters = next(
            call for call in driver.session_instance.calls if "MERGE (incident:Incident" in call[0]
        )
        self.assertEqual(parameters["providers"], ["stripe"])
        self.assertEqual(parameters["decline_codes"], ["DO_NOT_HONOR", "ISSUER_UNAVAILABLE"])
        self.assertIn("MERGE (provider:Provider {provider_id: provider_id})", query)
        self.assertIn("FOREACH (provider_id IN $providers", query)
        self.assertIn("OBSERVED_REFUSAL_CODE", query)


if __name__ == "__main__":
    unittest.main()

