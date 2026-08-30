"""Contract-oriented domain values for CTR-INC-001 and CTR-MEM-001 v1.1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping


class MemoryStatus(StrEnum):
    MATCH_FOUND = "MATCH_FOUND"
    NO_PRECEDENT = "NO_PRECEDENT"
    MEMORY_UNAVAILABLE = "MEMORY_UNAVAILABLE"


def _as_strings(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(str(item) for item in value)
    return (str(value),)


def _scope(value: object) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): _as_strings(item) for key, item in value.items()}


@dataclass(frozen=True)
class Incident:
    incident_id: str
    detected_at: datetime
    scope: dict[str, tuple[str, ...]]
    metrics: Mapping[str, Any]
    root_cause_status: str
    root_cause_category: str | None
    evidence_ids: tuple[str, ...]
    correlation_id: str

    @classmethod
    def from_contract(cls, payload: Mapping[str, Any]) -> "Incident":
        root_cause = payload["root_cause"]
        evidence = payload.get("evidence", ())
        return cls(
            incident_id=str(payload["incident_id"]),
            detected_at=datetime.fromisoformat(str(payload["detected_at"]).replace("Z", "+00:00")),
            scope=_scope(payload.get("scope")),
            metrics=dict(payload.get("metrics", {})),
            root_cause_status=str(root_cause["status"]),
            root_cause_category=root_cause.get("category"),
            evidence_ids=tuple(str(item["evidence_id"]) for item in evidence),
            correlation_id=str(payload["correlation_id"]),
        )


@dataclass(frozen=True)
class HistoricalIncident:
    incident_id: str
    occurred_at: datetime
    scope: dict[str, tuple[str, ...]]
    metrics: Mapping[str, Any]
    confirmation: str
    confirmed_cause: str
    prior_playbook_id: str
    evidence_ids: tuple[str, ...]
    provenance: str = "REAL_HUMAN_REVIEW"


@dataclass(frozen=True)
class SimilarIncidentMatch:
    incident_id: str
    occurred_at: datetime
    confirmation: str
    structured_score: float
    matching_factors: tuple[str, ...]
    different_factors: tuple[str, ...]
    confirmed_cause: str
    prior_playbook_id: str
    evidence_ids: tuple[str, ...]
    semantic_score: float | None = None

    def to_contract(self) -> dict[str, object]:
        return {
            "incident_id": self.incident_id,
            "occurred_at": self.occurred_at.isoformat(),
            "confirmation": self.confirmation,
            "structured_score": self.structured_score,
            "semantic_score": self.semantic_score,
            "matching_factors": list(self.matching_factors),
            "different_factors": list(self.different_factors),
            "confirmed_cause": self.confirmed_cause,
            "prior_playbook_id": self.prior_playbook_id,
            "evidence_ids": list(self.evidence_ids),
        }


@dataclass(frozen=True)
class RetrievalTrace:
    cypher_filter: str
    candidate_count: int
    embedding_model: str | None
    index_version: str
    fallback_used: bool

    def to_contract(self) -> dict[str, object]:
        return {
            "cypher_filter": self.cypher_filter,
            "candidate_count": self.candidate_count,
            "embedding_model": self.embedding_model,
            "index_version": self.index_version,
            "fallback_used": self.fallback_used,
        }


@dataclass(frozen=True)
class SimilarIncidentResult:
    query_incident_id: str
    memory_status: MemoryStatus
    matches: tuple[SimilarIncidentMatch, ...]
    retrieval_trace: RetrievalTrace
    correlation_id: str

    def __post_init__(self) -> None:
        if self.memory_status is MemoryStatus.MATCH_FOUND and not self.matches:
            raise ValueError("MATCH_FOUND requires at least one match")
        if self.memory_status is not MemoryStatus.MATCH_FOUND and self.matches:
            raise ValueError("non-match memory states require an empty matches list")

    def to_contract(self) -> dict[str, object]:
        return {
            "schema_version": "1.1",
            "query_incident_id": self.query_incident_id,
            "memory_status": self.memory_status.value,
            "matches": [match.to_contract() for match in self.matches],
            "retrieval_trace": self.retrieval_trace.to_contract(),
            "correlation_id": self.correlation_id,
        }

