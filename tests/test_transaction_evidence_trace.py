from __future__ import annotations

import unittest

from app.explanation import resolve_transaction_evidence
from tests.test_memory_service import current_incident


def transaction_record(
    transaction_id: str,
    *,
    correlation_id: str = "corr-001",
    incident_ids: list[str] | None = None,
    evidence_ids: list[str] | None = None,
) -> dict[str, object]:
    return {
        "transaction_id": transaction_id,
        "correlation_id": correlation_id,
        "classification": {
            "related_incident_ids": incident_ids if incident_ids is not None else ["INC-CURRENT-001"],
            "evidence_ids": evidence_ids if evidence_ids is not None else ["EVID-CURRENT-001"],
        },
    }


class TransactionEvidenceTraceTest(unittest.TestCase):
    def test_resolves_multiple_transactions_by_authorized_classification_evidence(self) -> None:
        incident = current_incident()
        trace = resolve_transaction_evidence(
            incident,
            [
                transaction_record("txn-002", evidence_ids=["evt-txn-002"]),
                transaction_record("txn-001", evidence_ids=["evt-txn-001", "evt-txn-001b"]),
            ],
        )

        self.assertEqual("INC-CURRENT-001", trace.incident_id)
        self.assertEqual(("txn-001", "txn-002"), trace.transaction_ids)
        self.assertEqual(("evt-txn-001", "evt-txn-001b", "evt-txn-002"), trace.evidence_ids)

    def test_rejects_cross_transaction_leakage_and_missing_evidence(self) -> None:
        incident = current_incident()
        trace = resolve_transaction_evidence(
            incident,
            [
                transaction_record("wrong-correlation", correlation_id="corr-other"),
                transaction_record("wrong-incident", incident_ids=["INC-OTHER"]),
                transaction_record("missing-evidence", evidence_ids=[]),
                {"transaction_id": "processing", "correlation_id": "corr-001", "classification": None},
            ],
        )

        self.assertEqual((), trace.transaction_ids)
        self.assertEqual((), trace.evidence_ids)

    def test_inconclusive_incident_remains_traceable_without_promotion(self) -> None:
        incident = current_incident(status="INCONCLUSIVE")
        trace = resolve_transaction_evidence(incident, [transaction_record("txn-inconclusive")])

        self.assertEqual("INCONCLUSIVE", incident.root_cause_status)
        self.assertEqual(("txn-inconclusive",), trace.transaction_ids)


if __name__ == "__main__":
    unittest.main()
