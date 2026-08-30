"""TASK-RCA-001 / LUM2-54 hierarchical, deterministic slice exploration.

This module ranks *hypotheses*, not confirmed causes.  It consumes only the
numeric ``CTR-DET-001`` candidate contract and deliberately has no dependency on
raw events, ground truth, Incident serialization, or retrieval.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from math import isfinite
from typing import Any

from pydantic import BaseModel

from app.detection.models import AnomalyCandidate

DEFAULT_DIMENSION_ORDER = (
    "provider_id",
    "country",
    "payment_method_category",
    "issuer_bank",
    "decline_code",
)


@dataclass(frozen=True)
class RcaHypothesis:
    """A pruned path in the RCA search tree, never a root-cause assertion."""

    correlation_id: str
    slice: dict[str, str]
    score: float
    support: int
    candidate_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]


def explore_slices(
    candidates: Iterable[AnomalyCandidate | Mapping[str, Any] | BaseModel],
    *,
    beam_width: int = 3,
    min_support: int = 12,
    dimension_order: Sequence[str] = DEFAULT_DIMENSION_ORDER,
    correlation_id: str | None = None,
) -> list[RcaHypothesis]:
    """Explore the strongest candidate slices with top-down beam pruning.

    All input must belong to one correlation group.  Keeping simultaneous groups
    separate avoids the false causal merge that Incident correlation explicitly
    protects against.  A return value is an ordered list of hypotheses at the
    deepest searchable level; an empty list is an honest insufficient-evidence
    result.
    """
    if not isinstance(beam_width, int) or isinstance(beam_width, bool) or beam_width < 1:
        raise ValueError("beam_width must be a positive integer")
    if not isinstance(min_support, int) or isinstance(min_support, bool) or min_support < 1:
        raise ValueError("min_support must be a positive integer")
    if not dimension_order or len(set(dimension_order)) != len(dimension_order):
        raise ValueError("dimension_order must contain unique dimensions")

    normalized = [_as_candidate(candidate) for candidate in candidates]
    if not normalized:
        return []
    available_correlations = {str(candidate["correlation_id"]) for candidate in normalized}
    if correlation_id is None:
        if len(available_correlations) != 1:
            raise ValueError("candidates from different correlation groups must be explored separately")
        correlation_id = available_correlations.pop()
    normalized = [candidate for candidate in normalized if candidate["correlation_id"] == correlation_id]
    if not normalized:
        return []

    beam: list[dict[str, str]] = [{}]
    last_hypotheses: list[RcaHypothesis] = []
    for dimension in dimension_order:
        expanded: list[RcaHypothesis] = []
        for prefix in beam:
            values = sorted(
                {
                    str(candidate["slice"][dimension])
                    for candidate in normalized
                    if _matches(candidate, prefix) and dimension in candidate["slice"]
                }
            )
            for value in values:
                next_prefix = {**prefix, dimension: value}
                hypothesis = _hypothesis_for(normalized, correlation_id, next_prefix, min_support)
                if hypothesis is not None:
                    expanded.append(hypothesis)
        if not expanded:
            break
        expanded.sort(key=_sort_key)
        last_hypotheses = expanded[:beam_width]
        beam = [hypothesis.slice for hypothesis in last_hypotheses]
    return last_hypotheses


def _as_candidate(candidate: AnomalyCandidate | Mapping[str, Any] | BaseModel) -> dict[str, Any]:
    payload = candidate.model_dump() if isinstance(candidate, BaseModel) else dict(candidate)
    slice_values = payload.get("slice")
    if not isinstance(slice_values, Mapping) or not slice_values:
        raise ValueError("candidate slice is required")
    if not isinstance(payload.get("candidate_id"), str) or not payload["candidate_id"]:
        raise ValueError("candidate_id is required")
    if not isinstance(payload.get("correlation_id"), str) or not payload["correlation_id"]:
        raise ValueError("correlation_id is required")
    if not isinstance(payload.get("sample_size"), int) or isinstance(payload["sample_size"], bool):
        raise ValueError("candidate sample_size must be an integer")
    if payload["sample_size"] < 0:
        raise ValueError("candidate sample_size must not be negative")
    return {**payload, "slice": {str(key): str(value) for key, value in slice_values.items()}}


def _matches(candidate: Mapping[str, Any], prefix: Mapping[str, str]) -> bool:
    return all(candidate["slice"].get(dimension) == value for dimension, value in prefix.items())


def _hypothesis_for(
    candidates: list[dict[str, Any]], correlation_id: str, prefix: dict[str, str], min_support: int
) -> RcaHypothesis | None:
    matching = [candidate for candidate in candidates if _matches(candidate, prefix)]
    support = max((candidate["sample_size"] for candidate in matching), default=0)
    if support < min_support:
        return None
    scores = [_candidate_score(candidate) for candidate in matching]
    evidence_refs = tuple(sorted({ref for candidate in matching for ref in candidate.get("evidence_refs", []) if ref}))
    return RcaHypothesis(
        correlation_id=correlation_id,
        slice=dict(prefix),
        score=max(scores, default=0.0),
        support=support,
        candidate_ids=tuple(sorted(candidate["candidate_id"] for candidate in matching)),
        evidence_refs=evidence_refs,
    )


def _candidate_score(candidate: Mapping[str, Any]) -> float:
    effect = abs(_finite_float(candidate.get("effect_relative")))
    strength = _unit_interval(_finite_float(candidate.get("statistical_strength")))
    quality = _unit_interval(_finite_float(candidate.get("data_quality"), default=1.0))
    coverage = _unit_interval(_finite_float(candidate.get("loss_coverage")))
    # Non-approval signals legitimately have zero lost-approval coverage; retain a
    # bounded contribution so latency/timeout candidates can still be explored.
    return min(1.0, effect * strength * quality * (0.25 + 0.75 * coverage))


def _finite_float(value: Any, *, default: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    return numeric if isfinite(numeric) else default


def _unit_interval(value: float) -> float:
    return max(0.0, min(1.0, value))


def _sort_key(hypothesis: RcaHypothesis) -> tuple[float, int, tuple[tuple[str, str], ...]]:
    return (-hypothesis.score, -hypothesis.support, tuple(sorted(hypothesis.slice.items())))
