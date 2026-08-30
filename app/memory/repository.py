"""Ports and a deterministic fallback repository for incident memory."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from .models import HistoricalIncident, Incident


class IncidentMemoryRepository(Protocol):
    def health(self) -> bool: ...

    def upsert(self, incident: HistoricalIncident) -> None: ...

    def confirmed_incidents(self, query: Incident | None = None) -> Iterable[HistoricalIncident]: ...


class InMemoryIncidentRepository:
    """Idempotent fallback used when the graph service is unavailable."""

    def __init__(self, *, available: bool = True, include_evaluation: bool = True) -> None:
        self.available = available
        self.include_evaluation = include_evaluation
        self._incidents: dict[str, HistoricalIncident] = {}

    def health(self) -> bool:
        return self.available

    def upsert(self, incident: HistoricalIncident) -> None:
        if not self.available:
            raise RuntimeError("memory repository unavailable")
        self._incidents[incident.incident_id] = incident

    def confirmed_incidents(self, query: Incident | None = None) -> Iterable[HistoricalIncident]:
        if not self.available:
            raise RuntimeError("memory repository unavailable")
        return tuple(
            incident
            for incident in self._incidents.values()
            if incident.confirmation == "HUMAN_CONFIRMED"
            or (self.include_evaluation and incident.confirmation == "EVALUATION_CONFIRMED")
        )

    @property
    def incident_count(self) -> int:
        return len(self._incidents)

