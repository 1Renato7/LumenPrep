from __future__ import annotations

import pytest

from app.rca import explore_slices


def _candidate(
    candidate_id: str,
    *,
    slice: dict[str, str],
    effect: float = -0.4,
    strength: float = 0.95,
    support: int = 100,
    correlation_id: str = "corr-rca-001",
) -> dict:
    return {
        "candidate_id": candidate_id,
        "correlation_id": correlation_id,
        "slice": slice,
        "effect_relative": effect,
        "statistical_strength": strength,
        "data_quality": 0.98,
        "loss_coverage": 0.8,
        "sample_size": support,
        "evidence_refs": [f"evidence://{candidate_id}"],
    }


def test_beam_search_returns_the_dominant_deepest_slice_deterministically():
    candidates = [
        _candidate("cand-stripe-br", slice={"provider_id": "stripe", "country": "BR"}, effect=-0.55),
        _candidate("cand-stripe-mx", slice={"provider_id": "stripe", "country": "MX"}, effect=-0.15),
        _candidate("cand-adyen-br", slice={"provider_id": "adyen", "country": "BR"}, effect=-0.25),
    ]

    first = explore_slices(candidates, beam_width=2, min_support=12)
    second = explore_slices(candidates, beam_width=2, min_support=12)

    assert first == second
    assert first[0].slice == {"provider_id": "stripe", "country": "BR"}
    assert first[0].candidate_ids == ("cand-stripe-br",)
    assert first[0].evidence_refs == ("evidence://cand-stripe-br",)


def test_beam_search_prunes_low_support_without_inventing_a_hypothesis():
    candidates = [
        _candidate("cand-supported", slice={"provider_id": "stripe", "country": "BR"}, support=100),
        _candidate("cand-sparse", slice={"provider_id": "adyen", "country": "MX"}, support=4, effect=-0.9),
    ]

    hypotheses = explore_slices(candidates, min_support=12)

    assert [hypothesis.slice for hypothesis in hypotheses] == [{"provider_id": "stripe", "country": "BR"}]


def test_no_anomaly_candidate_produces_no_rca_hypothesis():
    assert explore_slices([]) == []


@pytest.mark.parametrize("beam_width,min_support", [(1.5, 12), (2, 2.5), (True, 12)])
def test_search_parameters_must_be_positive_integers(beam_width: object, min_support: object):
    with pytest.raises(ValueError):
        explore_slices([], beam_width=beam_width, min_support=min_support)  # type: ignore[arg-type]


def test_beam_search_rejects_mixed_correlation_groups():
    candidates = [
        _candidate("cand-one", slice={"provider_id": "stripe"}),
        _candidate("cand-two", slice={"provider_id": "adyen"}, correlation_id="corr-rca-002"),
    ]

    with pytest.raises(ValueError, match="correlation groups"):
        explore_slices(candidates)
