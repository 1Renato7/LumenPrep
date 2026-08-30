"""CTR-INC-001 v1 incident correlation, impact, and serialization.

The RCA owner supplies root-cause status/category. This package never upgrades
an ``INCONCLUSIVE`` diagnosis from similarity or local heuristics.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from math import ceil
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Candidate = Mapping[str, Any]

# Which metric a detector candidate measured decides how its observed/expected
# pair may be named. Publishing a p95 in milliseconds as ``approval_rate_*``
# broke the 0..1 bound CTR-AGT-001 declares for those fields and handed the
# agent a "rate" of 2533. The latency keys match the vocabulary already used in
# contracts/fixtures/incident-mastercard-recurrence.json.
METRIC_SERIES_KEYS: dict[str, tuple[str, str]] = {
    "APPROVAL_RATE": ("approval_rate_observed", "approval_rate_expected"),
    "LATENCY_P95": ("provider_latency_p95_ms_observed", "provider_latency_p95_ms_expected"),
    "TIMEOUT_RATE": ("timeout_rate_observed", "timeout_rate_expected"),
    # PAYMENT_CONVERSION's own observed/expected are written again below by its
    # dedicated block, which is also where the web client reads them
    # (web/components/incidents/incidents.tsx). Mapping the pair here too keeps
    # this generic assignment from ever emitting the placeholder "observed" /
    # "expected" keys when a conversion candidate leads its group.
    "PAYMENT_CONVERSION": ("payment_conversion_observed", "payment_conversion_expected"),
}


def _as_dict(value: Candidate | BaseModel) -> dict[str, Any]:
    return value.model_dump() if isinstance(value, BaseModel) else dict(value)


def _window_overlaps(left: Candidate, right: Candidate) -> bool:
    try:
        left_window = left["window"]
        right_window = right["window"]
        return max(left_window["start"], right_window["start"]) < min(left_window["end"], right_window["end"])
    except (KeyError, TypeError):
        return False


def _causal_fingerprint(candidate: Candidate) -> tuple[tuple[str, str], ...] | None:
    """Canonicalize the full causal slice; partial overlap is not causality."""
    slice_values = candidate.get("slice")
    if not isinstance(slice_values, Mapping) or not slice_values:
        return None
    return tuple(sorted((str(dimension), str(value)) for dimension, value in slice_values.items()))


def _slices_compatible(left: Candidate, right: Candidate) -> bool:
    left_fingerprint = _causal_fingerprint(left)
    return left_fingerprint is not None and left_fingerprint == _causal_fingerprint(right)


@dataclass(frozen=True)
class CorrelatedCandidates:
    """Deterministic cluster of overlapping, non-conflicting RCA candidates."""

    candidates: tuple[dict[str, Any], ...]
    correlation_id: str

    @property
    def scope(self) -> dict[str, list[str]]:
        values: dict[str, set[str]] = {}
        for candidate in self.candidates:
            for dimension, value in candidate.get("slice", {}).items():
                values.setdefault(dimension, set()).add(str(value))
        return {dimension: sorted(value) for dimension, value in sorted(values.items())}

    @property
    def priority_score(self) -> float:
        """Rank within a correlation group; this is never presented as a cause."""
        return max(
            float(candidate.get("lost_approvals", 0))
            * float(candidate.get("statistical_strength", 0))
            * float(candidate.get("loss_coverage", 0))
            for candidate in self.candidates
        )


def correlate_candidates(candidates: Iterable[Candidate | BaseModel]) -> list[CorrelatedCandidates]:
    """Separate simultaneous RCA candidates into independent incident groups."""
    remaining = [_as_dict(candidate) for candidate in candidates]
    groups: list[CorrelatedCandidates] = []
    while remaining:
        seed = remaining.pop(0)
        cluster = [seed]
        changed = True
        while changed:
            changed = False
            for candidate in remaining[:]:
                if any(
                    candidate.get("correlation_id")
                    and candidate.get("correlation_id") == member.get("correlation_id")
                    and _window_overlaps(candidate, member)
                    and _slices_compatible(candidate, member)
                    for member in cluster
                ):
                    cluster.append(candidate)
                    remaining.remove(candidate)
                    changed = True
        groups.append(CorrelatedCandidates(tuple(cluster), str(seed.get("correlation_id", ""))))
    return sorted(groups, key=lambda group: group.priority_score, reverse=True)


class Impact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric: Literal["GMV_AT_RISK"] = "GMV_AT_RISK"
    amount_minor: int = Field(ge=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    method: Literal["EXPECTED_APPROVAL_SHORTFALL"] = "EXPECTED_APPROVAL_SHORTFALL"
    lower_bound_minor: int | None = Field(default=None, ge=0)
    upper_bound_minor: int | None = Field(default=None, ge=0)


def compute_impact(correlated: CorrelatedCandidates, window_metrics: Mapping[str, Any] | BaseModel) -> Impact:
    """Estimate local GMV at risk from the current window's observed ticket size.

    Multiple correlated candidates can describe the same lost approvals, so the
    maximum shortfall is used to avoid double-counting. Bounds remain null until
    the RCA owner supplies an uncertainty model.
    """
    metrics = _as_dict(window_metrics)
    eligible_attempts = int(metrics["eligible_attempts"])
    amount_minor = int(metrics["amount_minor"])
    if eligible_attempts <= 0:
        raise ValueError("eligible_attempts must be positive to estimate GMV at risk")
    lost_approvals = max(float(candidate.get("lost_approvals", 0)) for candidate in correlated.candidates)
    estimated_minor = ceil((amount_minor / eligible_attempts) * max(lost_approvals, 0))
    return Impact(amount_minor=estimated_minor, currency=str(metrics["currency"]))


class RootCauseAlternative(BaseModel):
    """A competing causal hypothesis, never an upgrade of the current cause."""

    model_config = ConfigDict(extra="forbid")

    category: str
    confidence: float = Field(ge=0, le=1)


class RootCause(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SUPPORTED", "INCONCLUSIVE"]
    category: str | None
    confidence: float = Field(ge=0, le=1)
    confidence_factors: dict[str, float]
    alternatives: list[RootCauseAlternative] = Field(default_factory=list)

    @model_validator(mode="after")
    def sort_alternatives(self) -> "RootCause":
        """Give every consumer a stable, confidence-first ordering."""
        self.alternatives.sort(key=lambda alternative: (-alternative.confidence, alternative.category))
        return self


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    kind: str
    statement: str
    source_ref: str


class Recommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    playbook_id: str
    action: str
    recommendation_class: Literal["INVESTIGATE", "MONITOR", "ESCALATE"] = "INVESTIGATE"
    execution: Literal["HUMAN_ONLY"] = "HUMAN_ONLY"
    rationale_evidence_ids: list[str]


class Incident(BaseModel):
    """Pydantic representation of ``contracts/v1/incident.schema.json``."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    incident_id: str
    state: Literal["DETECTED", "INVESTIGATING", "SUPPORTED", "INCONCLUSIVE", "RECOVERED", "HUMAN_CONFIRMED", "CLOSED"]
    detected_at: str
    estimated_started_at: str
    title: str
    scope: dict[str, list[str]]
    metrics: dict[str, Any]
    root_cause: RootCause
    impact: Impact
    evidence: list[Evidence]
    memory_matches: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[Recommendation]
    limitations: list[str]
    correlation_id: str

    @model_validator(mode="after")
    def keep_terminal_state_aligned_with_root_cause(self) -> "Incident":
        if self.state in {"SUPPORTED", "INCONCLUSIVE"} and self.state != self.root_cause.status:
            raise ValueError("state must match root_cause.status for supported or inconclusive incidents")
        return self


def prioritize_incidents_by_local_impact(incidents: Iterable[Incident]) -> dict[str, list[Incident]]:
    """Rank incidents by GMV at risk within their own currency only.

    ``amount_minor`` has no cross-currency meaning.  Bucketing is therefore the
    honest fallback until a versioned FX source is introduced.
    """
    buckets: dict[str, list[Incident]] = {}
    for incident in incidents:
        buckets.setdefault(incident.impact.currency, []).append(incident)
    return {
        currency: sorted(bucket, key=lambda incident: (-incident.impact.amount_minor, incident.incident_id))
        for currency, bucket in sorted(buckets.items())
    }


def to_incident(
    correlated: CorrelatedCandidates,
    impact: Impact,
    root_cause: RootCause | Mapping[str, Any],
    *,
    incident_id: str,
    title: str,
    evidence: Iterable[Evidence | Mapping[str, Any]],
    recommendations: Iterable[Recommendation | Mapping[str, Any]],
    limitations: Iterable[str] = (),
    detected_at: str | None = None,
    estimated_started_at: str | None = None,
    decline_codes: Iterable[str] = (),
) -> Incident:
    """Serialize an incident without changing the RCA-owned diagnosis."""
    cause = root_cause if isinstance(root_cause, RootCause) else RootCause.model_validate(root_cause)
    first_window = correlated.candidates[0].get("window", {})
    started = estimated_started_at or str(first_window.get("start") or datetime.now(timezone.utc).isoformat())
    detected = detected_at or str(first_window.get("end") or datetime.now(timezone.utc).isoformat())
    candidate = correlated.candidates[0]
    metric = str(candidate.get("metric") or "APPROVAL_RATE")
    observed_key, expected_key = METRIC_SERIES_KEYS.get(metric, ("observed", "expected"))
    metrics = {
        "eligible_attempts": int(candidate.get("sample_size", 0)),
        "metric": metric,
        observed_key: candidate.get("observed"),
        expected_key: candidate.get("expected"),
        "lost_approvals": int(round(max(float(item.get("lost_approvals", 0)) for item in correlated.candidates))),
    }
    conversion_candidates = [item for item in correlated.candidates if item.get("metric") == "PAYMENT_CONVERSION"]
    if conversion_candidates:
        conversion = conversion_candidates[0]
        metrics.update({
            "payment_conversion_observed": conversion.get("observed"),
            "payment_conversion_expected": conversion.get("expected"),
            "unique_payments": int(conversion.get("sample_size", 0)),
            "estimated_lost_conversions": int(round(float(conversion.get("estimated_lost_conversions", 0)))),
            "observation_window_minutes": 60,
        })
    normalized_declines = sorted({str(code) for code in decline_codes if str(code)})
    if normalized_declines:
        metrics["decline_codes"] = normalized_declines
    serialized_evidence = [item if isinstance(item, Evidence) else Evidence.model_validate(item) for item in evidence]
    serialized_recommendations = [
        item if isinstance(item, Recommendation) else Recommendation.model_validate(item) for item in recommendations
    ]
    return Incident(
        incident_id=incident_id,
        state=cause.status,
        detected_at=detected,
        estimated_started_at=started,
        title=title,
        scope=correlated.scope,
        metrics=metrics,
        root_cause=cause,
        impact=impact,
        evidence=serialized_evidence,
        recommendations=serialized_recommendations,
        limitations=list(limitations),
        correlation_id=correlated.correlation_id,
    )


from .repository import DuckDBIncidentRepository, IncidentIdConflictError, causal_fingerprint  # noqa: E402

__all__ = [
    "CorrelatedCandidates",
    "DuckDBIncidentRepository",
    "Evidence",
    "Impact",
    "Incident",
    "IncidentIdConflictError",
    "Recommendation",
    "RootCause",
    "RootCauseAlternative",
    "causal_fingerprint",
    "compute_impact",
    "correlate_candidates",
    "prioritize_incidents_by_local_impact",
    "to_incident",
]
