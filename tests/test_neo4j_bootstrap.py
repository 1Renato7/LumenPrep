from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.memory.neo4j_bootstrap import _statements, bootstrap


class FakeResult:
    def consume(self):
        return None


class FakeSession:
    def __init__(self):
        self.queries: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def run(self, query, **parameters):
        self.queries.append(query)
        return FakeResult()

    def execute_write(self, callback):
        return callback(self)


class FakeDriver:
    def __init__(self):
        self.session_instance = FakeSession()

    def session(self, **kwargs):
        return self.session_instance


class Neo4jBootstrapTest(unittest.TestCase):
    def test_statement_reader_ignores_comments(self):
        with TemporaryDirectory() as directory:
            cypher = Path(directory) / "constraints.cypher"
            cypher.write_text("// a comment\nCREATE (:Demo);\n\nCREATE (:Other);", encoding="utf-8")
            self.assertEqual(("CREATE (:Demo)", "CREATE (:Other)"), _statements(cypher))

    def test_bootstrap_applies_constraints_and_upserts_seed(self):
        driver = FakeDriver()
        incident_id = bootstrap(driver=driver)

        self.assertEqual("INC-HIST-002D-MASTERCARD", incident_id)
        self.assertTrue(any("CREATE CONSTRAINT incident_id" in query for query in driver.session_instance.queries))
        self.assertTrue(any("MERGE (incident:Incident" in query for query in driver.session_instance.queries))


if __name__ == "__main__":
    unittest.main()
