from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.memory import Incident, IncidentMemoryService, InMemoryIncidentRepository
from app.memory.promotion import IncidentPromoter, PromotionReview


def current_incident() -> Incident:
    return Incident(
        incident_id="inc-promotion-test-001",
        detected_at=datetime(2026, 8, 29, 12, tzinfo=timezone.utc),
        scope={"provider_id": ("stripe",), "country": ("BR",)},
        metrics={"approval_rate_observed": 0.36, "decline_codes": ["05"], "temporal_shape": "SUDDEN_STEP"},
        root_cause_status="INCONCLUSIVE",
        root_cause_category=None,
        evidence_ids=("evd-promotion-001",),
        correlation_id="corr-promotion-001",
    )


def review(*, provenance: str = "REAL_HUMAN_REVIEW") -> PromotionReview:
    return PromotionReview(
        review_id="review-promotion-001",
        incident_id="inc-promotion-test-001",
        reviewer_id="reviewer-001",
        confirmed_cause="PROVIDER_DEGRADATION",
        playbook_id="PB-ISSUER-INVESTIGATION",
        decline_codes=("05",),
        temporal_shape="SUDDEN_STEP",
        provenance=provenance,  # type: ignore[arg-type]
    )


class IncidentPromotionTest(unittest.TestCase):
    def test_real_review_promotes_idempotently(self) -> None:
        repository = InMemoryIncidentRepository()
        promoter = IncidentPromoter(repository)
        historical = promoter.promote(current_incident(), review())
        promoter.promote(current_incident(), review())
        self.assertEqual("HUMAN_CONFIRMED", historical.confirmation)
        self.assertEqual("REAL_HUMAN_REVIEW", historical.provenance)
        self.assertEqual(1, repository.incident_count)

    def test_synthetic_review_is_rejected_by_default(self) -> None:
        with self.assertRaises(PermissionError):
            IncidentPromoter(InMemoryIncidentRepository()).promote(
                current_incident(), review(provenance="SYNTHETIC_EVALUATION")
            )

    def test_synthetic_review_never_crosses_the_public_precedent_boundary(self) -> None:
        repository = InMemoryIncidentRepository(include_evaluation=True)
        IncidentPromoter(repository, allow_synthetic_evaluation=True).promote(
            current_incident(), review(provenance="SYNTHETIC_EVALUATION")
        )
        query = Incident(
            incident_id="inc-promotion-query-001",
            detected_at=datetime(2026, 8, 29, 12, 5, tzinfo=timezone.utc),
            scope=current_incident().scope,
            metrics=current_incident().metrics,
            root_cause_status="INCONCLUSIVE",
            root_cause_category=None,
            evidence_ids=("evd-promotion-query-001",),
            correlation_id="corr-promotion-query-001",
        )
        result = IncidentMemoryService(repository).retrieve(query)
        self.assertEqual("NO_PRECEDENT", result.memory_status.value)


if __name__ == "__main__":
    unittest.main()
