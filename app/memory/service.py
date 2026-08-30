"""Deterministic, explainable retrieval before optional vector reranking."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import timedelta

from .models import (
    HistoricalIncident,
    Incident,
    MemoryStatus,
    RetrievalTrace,
    SimilarIncidentMatch,
    SimilarIncidentResult,
)
from .repository import IncidentMemoryRepository


class IncidentMemoryService:
    def __init__(
        self,
        primary: IncidentMemoryRepository,
        *,
        fallback: IncidentMemoryRepository | None = None,
        threshold: float = 0.8,
        top_k: int = 3,
        lookback_days: int = 30,
    ) -> None:
        self.primary = primary
        self.fallback = fallback
        self.threshold = threshold
        self.top_k = top_k
        self.lookback_days = lookback_days

    def retrieve(self, incident: Incident) -> SimilarIncidentResult:
        repository, fallback_used = self._select_repository()
        if repository is None:
            return self._unavailable(incident)

        try:
            candidates = self._compatible_candidates(repository, incident)
        except Exception:
            if not fallback_used and self._healthy(self.fallback):
                repository = self.fallback
                fallback_used = True
                try:
                    candidates = self._compatible_candidates(repository, incident)
                except Exception:
                    return self._unavailable(incident, fallback_used=True)
            else:
                return self._unavailable(incident, fallback_used=fallback_used)

        matches = tuple(
            sorted(
                (self._score(incident, candidate) for candidate in candidates),
                key=lambda match: (-match.structured_score, -match.occurred_at.timestamp(), match.incident_id),
            )[: self.top_k]
        )
        accepted = tuple(match for match in matches if match.structured_score >= self.threshold)
        status = MemoryStatus.MATCH_FOUND if accepted else MemoryStatus.NO_PRECEDENT
        return SimilarIncidentResult(
            query_incident_id=incident.incident_id,
            memory_status=status,
            matches=accepted,
            retrieval_trace=RetrievalTrace(
                cypher_filter="confirmation = 'HUMAN_CONFIRMED' AND shared_scope = true",
                candidate_count=len(candidates),
                embedding_model=None,
                index_version="structured-v1",
                fallback_used=fallback_used,
            ),
            correlation_id=incident.correlation_id,
        )

    def _select_repository(self) -> tuple[IncidentMemoryRepository | None, bool]:
        if self._healthy(self.primary):
            return self.primary, False
        if self._healthy(self.fallback):
            return self.fallback, True
        return None, False

    @staticmethod
    def _healthy(repository: IncidentMemoryRepository | None) -> bool:
        if repository is None:
            return False
        try:
            return repository.health()
        except Exception:
            return False

    def _compatible_candidates(
        self, repository: IncidentMemoryRepository, incident: Incident
    ) -> tuple[HistoricalIncident, ...]:
        cutoff = incident.detected_at - timedelta(days=self.lookback_days)
        return tuple(
            candidate
            for candidate in repository.confirmed_incidents(incident)
            if candidate.confirmation == "HUMAN_CONFIRMED"
            and candidate.incident_id != incident.incident_id
            and cutoff <= candidate.occurred_at <= incident.detected_at
            and _shares_scope(incident, candidate)
        )

    def _unavailable(self, incident: Incident, *, fallback_used: bool = False) -> SimilarIncidentResult:
        return SimilarIncidentResult(
            query_incident_id=incident.incident_id,
            memory_status=MemoryStatus.MEMORY_UNAVAILABLE,
            matches=(),
            retrieval_trace=RetrievalTrace(
                cypher_filter="confirmation = 'HUMAN_CONFIRMED' AND shared_scope = true",
                candidate_count=0,
                embedding_model=None,
                index_version="structured-v1",
                fallback_used=fallback_used,
            ),
            correlation_id=incident.correlation_id,
        )

    def _score(self, incident: Incident, candidate: HistoricalIncident) -> SimilarIncidentMatch:
        factors, differences, score = _structured_similarity(incident, candidate)
        return SimilarIncidentMatch(
            incident_id=candidate.incident_id,
            occurred_at=candidate.occurred_at,
            confirmation=candidate.confirmation,
            structured_score=round(score, 4),
            matching_factors=tuple(factors),
            different_factors=tuple(differences),
            confirmed_cause=candidate.confirmed_cause,
            prior_playbook_id=candidate.prior_playbook_id,
            evidence_ids=candidate.evidence_ids,
        )


def _structured_similarity(incident: Incident, candidate: HistoricalIncident) -> tuple[list[str], list[str], float]:
    factors: list[str] = []
    differences: list[str] = []
    score_parts: list[tuple[float, float]] = []

    scoped = [key for key in incident.scope if incident.scope[key]]
    if scoped:
        matches = 0
        for key in scoped:
            current = set(incident.scope[key])
            historical = set(candidate.scope.get(key, ()))
            shared = current & historical
            if shared:
                matches += 1
                factors.append(f"scope.{key}={','.join(sorted(shared))}")
            else:
                differences.append(f"scope.{key}")
        score_parts.append((0.65, matches / len(scoped)))

    current_declines = set(_as_values(incident.metrics.get("decline_codes")))
    historical_declines = set(_as_values(candidate.metrics.get("decline_codes")))
    if current_declines:
        overlap = current_declines & historical_declines
        ratio = len(overlap) / len(current_declines | historical_declines) if historical_declines else 0.0
        if overlap:
            factors.append(f"decline_codes={','.join(sorted(overlap))}")
        else:
            differences.append("decline_codes")
        score_parts.append((0.2, ratio))

    current_shape = incident.metrics.get("temporal_shape")
    historical_shape = candidate.metrics.get("temporal_shape")
    if current_shape:
        same_shape = current_shape == historical_shape
        (factors if same_shape else differences).append(
            f"temporal_shape={current_shape}" if same_shape else "temporal_shape"
        )
        score_parts.append((0.15, 1.0 if same_shape else 0.0))

    denominator = sum(weight for weight, _ in score_parts)
    score = sum(weight * value for weight, value in score_parts) / denominator if denominator else 0.0
    return factors, differences, score


def _as_values(value: object) -> Iterable[str]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(str(item) for item in value)
    return (str(value),)


def _shares_scope(incident: Incident, candidate: HistoricalIncident) -> bool:
    return any(
        set(values) & set(candidate.scope.get(dimension, ()))
        for dimension, values in incident.scope.items()
        if values
    )

