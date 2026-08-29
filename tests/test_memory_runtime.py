from __future__ import annotations

import unittest

from app.memory import MemoryStatus, Neo4jSettings, create_memory_runtime
from tests.test_memory_service import current_incident


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def run(self, *args, **kwargs):
        raise RuntimeError("graph unavailable")


class FakeDriver:
    def __init__(self):
        self.closed = False

    def session(self, **kwargs):
        return FakeSession()

    def close(self):
        self.closed = True


class MemoryRuntimeTest(unittest.TestCase):
    def test_runtime_uses_neo4j_primary_and_seeded_fallback(self):
        driver = FakeDriver()
        captured: dict[str, object] = {}

        def factory(uri, auth):
            captured.update(uri=uri, auth=auth)
            return driver

        runtime = create_memory_runtime(
            Neo4jSettings(uri="bolt://graph:7687", user="neo4j", password="local-secret"),
            driver_factory=factory,
        )
        result = runtime.service.retrieve(current_incident())

        self.assertEqual("bolt://graph:7687", captured["uri"])
        self.assertEqual(("neo4j", "local-secret"), captured["auth"])
        self.assertEqual(MemoryStatus.MATCH_FOUND, result.memory_status)
        self.assertTrue(result.retrieval_trace.fallback_used)
        runtime.close()
        self.assertTrue(driver.closed)

    def test_settings_require_a_password(self):
        with self.assertRaisesRegex(RuntimeError, "NEO4J_PASSWORD"):
            Neo4jSettings.from_environment({})


if __name__ == "__main__":
    unittest.main()
