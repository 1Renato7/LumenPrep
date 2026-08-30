"""Explicit, provenance-gated promotion of current Incidents into memory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .models import HistoricalIncident, Incident
from .repository import IncidentMemoryRepository


@dataclass(frozen=True)
class PromotionReview:
    """Human review (production) or explicitly enabled evaluation review."""

    review_id: str
    incident_id: str
    reviewer_id: str
    confirmed_cause: str
    playbook_id: str
    decline_codes: tuple[str, ...]
    temporal_shape: str
    provenance: Literal["REAL_HUMAN_REVIEW", "SYNTHETIC_EVALUATION"]


class IncidentPromoter:
    """Promote only reviewed records; synthetic material is evaluation-only by default."""

    def __init__(self, repository: IncidentMemoryRepository, *, allow_synthetic_evaluation: bool = False) -> None:
        self.repository = repository
        self.allow_synthetic_evaluation = allow_synthetic_evaluation

    def promote(self, incident: Incident, review: PromotionReview) -> HistoricalIncident:
        if review.incident_id != incident.incident_id:
            raise ValueError("review must reference the Incident being promoted")
        if not review.reviewer_id or not review.review_id:
            raise ValueError("review_id and reviewer_id are required")
        if not review.confirmed_cause or not review.playbook_id:
            raise ValueError("confirmed cause and playbook are required")
        if not review.decline_codes or not review.temporal_shape:
            raise ValueError("decline_codes and temporal_shape are required")
        if review.provenance == "SYNTHETIC_EVALUATION" and not self.allow_synthetic_evaluation:
            raise PermissionError("synthetic evaluation records are disabled outside evaluation mode")

        evidence_ids = tuple(sorted(set(incident.evidence_ids)))
        if not evidence_ids:
            raise ValueError("promoted incidents require evidence")

        metrics = dict(incident.metrics)
        metrics.update(
            {
                "decline_codes": list(review.decline_codes),
                "temporal_shape": review.temporal_shape,
                "promotion": {
                    "review_id": review.review_id,
                    "reviewer_id": review.reviewer_id,
                    "provenance": review.provenance,
                },
            }
        )
        historical = HistoricalIncident(
            incident_id=incident.incident_id,
            occurred_at=incident.detected_at,
            scope=incident.scope,
            metrics=metrics,
            confirmation="HUMAN_CONFIRMED" if review.provenance == "REAL_HUMAN_REVIEW" else "EVALUATION_CONFIRMED",
            confirmed_cause=review.confirmed_cause,
            prior_playbook_id=review.playbook_id,
            evidence_ids=evidence_ids,
            provenance=review.provenance,
        )
        self.repository.upsert(historical)
        return historical
