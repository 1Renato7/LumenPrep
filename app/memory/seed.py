"""The deterministic D-2 Mastercard precedent required by the demo."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .models import HistoricalIncident
from .repository import IncidentMemoryRepository


def mastercard_d2_precedent(*, now: datetime | None = None) -> HistoricalIncident:
    reference = now or datetime.now(timezone.utc)
    return HistoricalIncident(
        incident_id="INC-HIST-002D-MASTERCARD",
        occurred_at=reference - timedelta(days=2),
        scope={
            "provider": ("stripe",),
            "country": ("BR",),
            "card_brand": ("MASTERCARD",),
        },
        metrics={
            "decline_codes": ["DO_NOT_HONOR", "ISSUER_UNAVAILABLE"],
            "temporal_shape": "sudden_approval_drop",
        },
        confirmation="HUMAN_CONFIRMED",
        confirmed_cause="ISSUER_OUTAGE",
        prior_playbook_id="PB-ISSUER-INVESTIGATION",
        evidence_ids=("EVID-HIST-MC-001", "EVID-HIST-MC-002"),
    )


def seed_mastercard_d2(repository: IncidentMemoryRepository, *, now: datetime | None = None) -> HistoricalIncident:
    incident = mastercard_d2_precedent(now=now)
    repository.upsert(incident)
    return incident

