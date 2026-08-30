"""TASK-RCA-002 / LUM2-55 deterministic ranking of RCA hypotheses.

The ranking orders investigation hypotheses.  It deliberately keeps the
serialized ``RootCause`` inconclusive because anomaly candidates alone do not
provide independent causal confirmation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

from app.incidents import RootCause, RootCauseAlternative

from .beam import RcaHypothesis

# Placeholders the cube writes when a dimension does not apply to an attempt.
# They identify the absence of a value, so they can never name a suspect.
ABSENT_DIMENSION_VALUES = frozenset({"NOT_APPLICABLE", "UNKNOWN", ""})


@dataclass(frozen=True)
class RankedHypothesis:
    """An RCA path with an auditable prioritization score."""

    hypothesis: RcaHypothesis
    category: str
    confidence: float
    contribution: float
    affected_share: float
    specificity: float


@dataclass(frozen=True)
class RcaRanking:
    """Ordered hypotheses plus an explicitly non-confirmatory contract handoff."""

    correlation_id: str | None
    ranked: tuple[RankedHypothesis, ...]
    winner: RankedHypothesis | None
    ambiguous: bool

    def to_root_cause(self, *, allow_supported: bool = False, minimum_confidence: float = 0.75) -> RootCause:
        """Serialize a conclusion only when the caller enables the evidence gate.

        The default remains conservative for existing consumers and tests. The
        live incident pipeline opts in after it has statistical candidates.
        """
        top = self.ranked[0] if self.ranked else None
        confidence_factors = (
            {
                "contribution": top.contribution,
                "affected_share": top.affected_share,
                "specificity": top.specificity,
                "dominance_margin": _dominance_margin(self.ranked),
            }
            if top is not None
            else {
                "contribution": 0.0,
                "affected_share": 0.0,
                "specificity": 0.0,
                "dominance_margin": 0.0,
            }
        )
        alternatives_by_category: dict[str, RootCauseAlternative] = {}
        for item in self.ranked:
            alternatives_by_category.setdefault(
                item.category,
                RootCauseAlternative(category=item.category, confidence=item.confidence),
            )
        supported = bool(allow_supported and self.winner is not None and self.winner.confidence >= minimum_confidence)
        return RootCause(
            status="SUPPORTED" if supported else "INCONCLUSIVE",
            category=self.winner.category if supported and self.winner is not None else None,
            confidence=top.confidence if top is not None else 0.0,
            confidence_factors=confidence_factors,
            alternatives=list(alternatives_by_category.values()),
        )


def rank_hypotheses(
    hypotheses: Iterable[RcaHypothesis], *, ambiguity_margin: float = 0.10
) -> RcaRanking:
    """Rank hypotheses by contribution, affected share and slice specificity.

    ``ambiguity_margin`` applies to the difference between the top two scores.
    Below it, no unique winner is returned.  Alternatives remain available in
    either case and callers must preserve the inconclusive causal status.
    """
    if not isinstance(ambiguity_margin, (int, float)) or isinstance(ambiguity_margin, bool):
        raise ValueError("ambiguity_margin must be a finite number between zero and one")
    if not isfinite(float(ambiguity_margin)) or not 0 <= ambiguity_margin < 1:
        raise ValueError("ambiguity_margin must be a finite number between zero and one")

    paths = list(hypotheses)
    if not paths:
        return RcaRanking(correlation_id=None, ranked=(), winner=None, ambiguous=False)
    correlation_ids = {path.correlation_id for path in paths}
    if len(correlation_ids) != 1:
        raise ValueError("hypotheses from different correlation groups must be ranked separately")

    if any(
        path.support < 1 or not path.slice or not isfinite(path.score)
        for path in paths
    ):
        raise ValueError("hypotheses must have positive support and a non-empty slice")
    max_support = max(path.support for path in paths)
    max_depth = max(len(path.slice) for path in paths)

    ranked = [
        _rank(path, max_support=max_support, max_depth=max_depth)
        for path in paths
    ]
    ranked.sort(key=_sort_key)
    ambiguous = len(ranked) > 1 and ranked[0].confidence - ranked[1].confidence < ambiguity_margin
    return RcaRanking(
        correlation_id=paths[0].correlation_id,
        ranked=tuple(ranked),
        winner=None if ambiguous else ranked[0],
        ambiguous=ambiguous,
    )


def _rank(path: RcaHypothesis, *, max_support: int, max_depth: int) -> RankedHypothesis:
    contribution = _unit_interval(path.score)
    affected_share = _unit_interval(path.support / max_support)
    specificity = _unit_interval(len(path.slice) / max_depth)
    # Weights sum to one and reward a material deviation more than reach or
    # dimensional detail, while keeping all terms bounded and inspectable.
    confidence = 0.55 * contribution + 0.25 * affected_share + 0.20 * specificity
    return RankedHypothesis(
        hypothesis=path,
        category=_category_for(path),
        confidence=confidence,
        contribution=contribution,
        affected_share=affected_share,
        specificity=specificity,
    )


def _category_for(path: RcaHypothesis) -> str:
    dimensions = path.slice
    if _names_an_issuer(dimensions):
        return "ISSUER_OUTAGE"
    if "provider_id" in dimensions:
        return "PROVIDER_DEGRADATION"
    if "payment_method_category" in dimensions:
        return "PAYMENT_METHOD_DEGRADATION"
    if "country" in dimensions:
        return "COUNTRY_LOCALIZED_DEGRADATION"
    if "merchant_id" in dimensions:
        return "MERCHANT_LOCALIZED_DEGRADATION"
    return "UNCLASSIFIED_DEGRADATION"


def _names_an_issuer(dimensions: dict[str, str]) -> bool:
    """A slice points at an issuer only when it actually carries one.

    ``app.aggregation.windows`` fills ``issuer_bank_id`` for every attempt,
    using ``NOT_APPLICABLE`` for methods that have no issuer at all (wallet,
    bank transfer). Testing for the key alone therefore attributed a wallet or
    bank-transfer degradation to an issuer that does not exist, and because
    this dimension is checked first it outranked every other explanation.
    """
    for key in ("issuer_bank_id", "issuer_bank"):
        value = dimensions.get(key)
        if value is not None and str(value) not in ABSENT_DIMENSION_VALUES:
            return True
    return False


def _dominance_margin(ranked: tuple[RankedHypothesis, ...]) -> float:
    if len(ranked) < 2:
        return 1.0 if ranked else 0.0
    return ranked[0].confidence - ranked[1].confidence


def _unit_interval(value: float) -> float:
    return max(0.0, min(1.0, value))


def _sort_key(item: RankedHypothesis) -> tuple[float, int, int, str, tuple[tuple[str, str], ...]]:
    return (
        -item.confidence,
        -item.hypothesis.support,
        -len(item.hypothesis.slice),
        item.category,
        tuple(sorted(item.hypothesis.slice.items())),
    )
