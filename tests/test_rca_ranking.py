from __future__ import annotations

import pytest

from app.rca import RcaHypothesis, rank_hypotheses


def _hypothesis(
    *,
    candidate_id: str,
    slice: dict[str, str],
    score: float = 0.7,
    support: int = 100,
) -> RcaHypothesis:
    return RcaHypothesis(
        correlation_id="corr-ranking-001",
        slice=slice,
        score=score,
        support=support,
        candidate_ids=(candidate_id,),
        evidence_refs=(f"evidence://{candidate_id}",),
    )


def test_ranking_selects_a_dominant_hypothesis_and_serializes_alternatives():
    result = rank_hypotheses(
        [
            _hypothesis(
                candidate_id="provider-br",
                slice={"provider_id": "stripe", "country": "BR"},
                score=0.92,
                support=95,
            ),
            _hypothesis(
                candidate_id="issuer-mx",
                slice={"issuer_bank": "issuer-mx"},
                score=0.28,
                support=20,
            ),
        ]
    )

    assert result.ambiguous is False
    assert result.winner is not None
    assert result.winner.category == "PROVIDER_DEGRADATION"
    assert [item.category for item in result.ranked] == ["PROVIDER_DEGRADATION", "ISSUER_OUTAGE"]

    root_cause = result.to_root_cause()
    assert root_cause.status == "INCONCLUSIVE"
    assert root_cause.category is None
    assert [item.category for item in root_cause.alternatives] == ["PROVIDER_DEGRADATION", "ISSUER_OUTAGE"]


def test_mix_shift_keeps_ordered_alternatives_without_claiming_supported_cause():
    result = rank_hypotheses(
        [
            _hypothesis(
                candidate_id="provider",
                slice={"provider_id": "stripe"},
                score=0.70,
                support=80,
            ),
            _hypothesis(
                candidate_id="method",
                slice={"payment_method_category": "CARD"},
                score=0.60,
                support=75,
            ),
        ],
        ambiguity_margin=0.02,
    )

    assert result.winner is not None
    assert result.to_root_cause().status == "INCONCLUSIVE"
    assert [item.category for item in result.to_root_cause().alternatives] == [
        "PROVIDER_DEGRADATION",
        "PAYMENT_METHOD_DEGRADATION",
    ]


def test_tie_is_inconclusive_and_has_no_unique_winner():
    result = rank_hypotheses(
        [
            _hypothesis(candidate_id="provider", slice={"provider_id": "stripe"}),
            _hypothesis(candidate_id="issuer", slice={"issuer_bank": "bank-a"}),
        ]
    )

    assert result.ambiguous is True
    assert result.winner is None
    assert result.to_root_cause().status == "INCONCLUSIVE"
    assert len(result.to_root_cause().alternatives) == 2


def test_empty_or_mixed_correlation_hypotheses_do_not_produce_a_cause():
    empty = rank_hypotheses([])
    assert empty.winner is None
    assert empty.to_root_cause().alternatives == []

    mixed = [
        _hypothesis(candidate_id="one", slice={"provider_id": "stripe"}),
        RcaHypothesis(
            correlation_id="corr-ranking-002",
            slice={"provider_id": "adyen"},
            score=0.7,
            support=100,
            candidate_ids=("two",),
            evidence_refs=("evidence://two",),
        ),
    ]
    with pytest.raises(ValueError, match="correlation groups"):
        rank_hypotheses(mixed)


@pytest.mark.parametrize("score,support", [(float("nan"), 100), (0.7, 0)])
def test_invalid_hypothesis_inputs_are_rejected(score: float, support: int):
    with pytest.raises(ValueError, match="positive support"):
        rank_hypotheses(
            [_hypothesis(candidate_id="invalid", slice={"provider_id": "stripe"}, score=score, support=support)]
        )
