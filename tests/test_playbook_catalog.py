from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.explanation import GroundedExplainer, load_playbooks
from app.memory import IncidentMemoryService, InMemoryIncidentRepository
from app.memory.seed import seed_mastercard_d2
from tests.test_memory_service import current_incident


class PlaybookCatalogTest(unittest.TestCase):
    def test_default_catalog_is_versioned_and_selects_issuer_playbook(self) -> None:
        playbooks = load_playbooks()
        ids = {playbook.playbook_id for playbook in playbooks}
        self.assertEqual({"PB-GENERIC-INVESTIGATION", "PB-ISSUER-INVESTIGATION"}, ids)

        repository = InMemoryIncidentRepository()
        seed_mastercard_d2(repository)
        memory = IncidentMemoryService(repository).retrieve(current_incident())
        bundle = GroundedExplainer(playbooks).explain(current_incident(), memory)

        self.assertEqual("PB-ISSUER-INVESTIGATION", bundle.playbook_id)
        self.assertEqual("HUMAN_ONLY", bundle.to_contract()["execution"])

    def test_catalog_rejects_non_human_execution(self) -> None:
        payload = {
            "schema_version": "1.0",
            "playbooks": [
                {
                    "playbook_id": "PB-GENERIC-INVESTIGATION",
                    "cause_categories": [],
                    "required_scope": {},
                    "action": "Execute a payment reroute.",
                    "cautions": ["Unsafe."],
                    "execution": "AUTOMATIC",
                }
            ],
        }
        with TemporaryDirectory() as directory:
            path = Path(directory) / "playbooks.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_playbooks(path)

    def test_catalog_rejects_unknown_root_fields_and_empty_scope_values(self) -> None:
        payload = {
            "schema_version": "1.0",
            "unexpected": True,
            "playbooks": [
                {
                    "playbook_id": "PB-GENERIC-INVESTIGATION",
                    "cause_categories": [],
                    "required_scope": {},
                    "action": "Inspect evidence.",
                    "cautions": ["Human review."],
                    "execution": "HUMAN_ONLY",
                }
            ],
        }
        with TemporaryDirectory() as directory:
            path = Path(directory) / "playbooks.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_playbooks(path)

            payload.pop("unexpected")
            payload["playbooks"][0]["required_scope"] = {"country": []}
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_playbooks(path)


if __name__ == "__main__":
    unittest.main()

