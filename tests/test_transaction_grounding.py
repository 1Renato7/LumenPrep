from __future__ import annotations

import unittest
from dataclasses import replace

from app.explanation import (
    ExplanationBundle,
    resolve_transaction_grounding,
    resolve_transaction_grounding_from_api_responses,
)
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
            "evidence_ids": evidence_ids if evidence_ids is not None else ["EVT-TXN-001"],
        },
    }


def explanation(incident_id: str, *, limitations: tuple[str, ...] = ()) -> ExplanationBundle:
    return ExplanationBundle(
        incident_id=incident_id,
        executive_summary=f"Summary for {incident_id}.",
        operations_summary="Review scoped evidence.",
        what_happened="An incident was observed.",
        where_and_why="Current evidence is available.",
        recurrence_statement=None,
        evidence_ids=("EVID-CURRENT-001",),
        playbook_id="PB-GENERIC-INVESTIGATION",
        recommended_action="Review the evidence.",
        limitations=limitations,
    )


class TransactionGroundingTest(unittest.TestCase):
    def test_api_response_adapter_reuses_existing_bundle(self) -> None:
        incident = current_incident()
        bundle = explanation(incident.incident_id)
        response = {
            "incident": {
                "incident_id": incident.incident_id,
                "detected_at": incident.detected_at.isoformat(),
                "scope": {key: list(value) for key, value in incident.scope.items()},
                "metrics": dict(incident.metrics),
                "root_cause": {"status": incident.root_cause_status, "category": incident.root_cause_category},
                "evidence": [{"evidence_id": item} for item in incident.evidence_ids],
                "correlation_id": incident.correlation_id,
            },
            "explanation": bundle.to_contract(),
        }

        result = resolve_transaction_grounding_from_api_responses(
            "txn-api", [transaction_record("txn-api")], {incident.incident_id: response}
        )

        self.assertEqual("RESOLVED", result.status)
        self.assertEqual(bundle.to_contract(), result.incident_links[0].explanation.to_contract())

    def test_api_response_adapter_keeps_invalid_bundle_explicit(self) -> None:
        incident = current_incident()
        response = {
            "incident": {
                "incident_id": incident.incident_id,
                "detected_at": incident.detected_at.isoformat(),
                "scope": {key: list(value) for key, value in incident.scope.items()},
                "metrics": dict(incident.metrics),
                "root_cause": {"status": incident.root_cause_status, "category": incident.root_cause_category},
                "evidence": [{"evidence_id": item} for item in incident.evidence_ids],
                "correlation_id": incident.correlation_id,
            },
            "explanation": {"incident_id": incident.incident_id},
        }

        result = resolve_transaction_grounding_from_api_responses(
            "txn-invalid-bundle", [transaction_record("txn-invalid-bundle")], {incident.incident_id: response}
        )

        self.assertEqual("PARTIAL", result.status)
        self.assertIn("invalid", result.incident_links[0].limitations[0])

    def test_no_incident_is_explicit_and_other_transactions_do_not_leak(self) -> None:
        incident = current_incident()
        result = resolve_transaction_grounding(
            "txn-target",
            [
                transaction_record("txn-other"),
                transaction_record("txn-target", incident_ids=["INC-MISSING"]),
                transaction_record("txn-target", correlation_id="corr-other"),
            ],
            {incident.incident_id: incident},
        )

        self.assertEqual("NO_INCIDENT", result.status)
        self.assertEqual((), result.incident_ids)
        self.assertEqual((), result.evidence_ids)
        self.assertIn("INC-MISSING", result.rejected_incident_ids)
        self.assertIn("No related Incident", result.short_summary)

    def test_one_incident_reuses_existing_bundle_and_only_exposes_transaction_evidence(self) -> None:
        incident = current_incident()
        bundle = explanation(incident.incident_id)
        result = resolve_transaction_grounding(
            "txn-001",
            [transaction_record("txn-001", evidence_ids=["EVT-TXN-001", "EVT-TXN-002"])],
            {incident.incident_id: incident},
            {incident.incident_id: bundle},
        )

        self.assertEqual("RESOLVED", result.status)
        self.assertEqual((incident.incident_id,), result.incident_ids)
        self.assertEqual(("EVT-TXN-001", "EVT-TXN-002"), result.evidence_ids)
        self.assertIs(bundle, result.incident_links[0].explanation)
        self.assertEqual(("EVID-CURRENT-001",), result.incident_links[0].incident_evidence_ids)
        self.assertNotIn("EVID-CURRENT-001", result.evidence_ids)
        self.assertEqual(bundle.executive_summary, result.short_summary)

    def test_multiple_incidents_are_sorted_and_scope_validated(self) -> None:
        first = current_incident()
        second = replace(first, incident_id="INC-CURRENT-002", correlation_id="corr-002")
        result = resolve_transaction_grounding(
            "txn-multi",
            [
                transaction_record("txn-multi", correlation_id="corr-002", incident_ids=[second.incident_id], evidence_ids=["EVT-2"]),
                transaction_record("txn-multi", incident_ids=[first.incident_id], evidence_ids=["EVT-1"]),
                transaction_record("txn-multi", incident_ids=["INC-OTHER"], evidence_ids=["EVT-X"]),
            ],
            [second, first],
            {first.incident_id: explanation(first.incident_id), second.incident_id: explanation(second.incident_id)},
        )

        self.assertEqual("PARTIAL", result.status)
        self.assertEqual((first.incident_id, second.incident_id), result.incident_ids)
        self.assertEqual(("EVT-1", "EVT-2"), result.evidence_ids)
        self.assertEqual(("INC-OTHER",), result.rejected_incident_ids)

    def test_missing_evidence_does_not_create_a_link(self) -> None:
        incident = current_incident()
        result = resolve_transaction_grounding(
            "txn-no-evidence",
            [transaction_record("txn-no-evidence", evidence_ids=[])],
            [incident],
        )

        self.assertEqual("NO_INCIDENT", result.status)
        self.assertEqual((incident.incident_id,), result.rejected_incident_ids)
        self.assertEqual((), result.incident_links)

    def test_memory_and_model_failures_remain_explicit(self) -> None:
        incident = current_incident()
        bundle = explanation(
            incident.incident_id,
            limitations=("Incident memory is unavailable; the current causal status is unchanged.",),
        )
        bundle = replace(bundle, model_version="deterministic-template")
        result = resolve_transaction_grounding(
            "txn-failure",
            [transaction_record("txn-failure")],
            [incident],
            {incident.incident_id: bundle},
        )

        link = result.incident_links[0]
        self.assertIn("Incident memory is unavailable", link.limitations[0])
        self.assertEqual("deterministic-template", link.explanation.model_version)
        self.assertNotIn("SUPPORTED", result.short_summary)

    def test_missing_bundle_is_reported_without_generating_one(self) -> None:
        incident = current_incident()
        result = resolve_transaction_grounding(
            "txn-model-down",
            [transaction_record("txn-model-down")],
            [incident],
            explanation_failures={incident.incident_id: "Model unavailable; deterministic ExplanationBundle was not supplied."},
        )

        self.assertEqual("PARTIAL", result.status)
        self.assertIsNone(result.incident_links[0].explanation)
        self.assertIn("Model unavailable", result.incident_links[0].limitations[0])
        self.assertIn("unavailable", result.short_summary)


if __name__ == "__main__":
    unittest.main()
