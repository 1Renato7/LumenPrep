from __future__ import annotations

import unittest

from app.incidents import CorrelatedCandidates, Impact, RootCause, to_incident
from app.worker.incident_pipeline import _memory_decline_codes


class CurrentIncidentGraphRagMetricsTest(unittest.TestCase):
    def test_detected_decline_profile_becomes_memory_metrics(self) -> None:
        decline_codes = _memory_decline_codes(
            {"NO_DECLINE": 8, "PROVIDER_TIMEOUT": 3, "UNMAPPED_DECLINE": 1}
        )
        incident = to_incident(
            CorrelatedCandidates(
                candidates=(
                    {
                        "slice": {"provider_id": "stripe", "country": "BR"},
                        "window": {"start": "2026-08-30T12:00:00Z", "end": "2026-08-30T12:05:00Z"},
                        "lost_approvals": 3,
                        "sample_size": 12,
                        "observed": 0.58,
                        "expected": 0.84,
                    },
                ),
                correlation_id="corr-graphrag-current-001",
            ),
            Impact(amount_minor=1000, currency="BRL"),
            RootCause(
                status="INCONCLUSIVE",
                category=None,
                confidence=0.4,
                confidence_factors={"test": 0.4},
            ),
            incident_id="inc-graphrag-current-001",
            title="GraphRAG metrics test",
            evidence=[],
            recommendations=[],
            decline_codes=decline_codes,
        )
        self.assertEqual(["PROVIDER_TIMEOUT"], incident.metrics["decline_codes"])


if __name__ == "__main__":
    unittest.main()
