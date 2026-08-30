import pytest

from app.incidents import CorrelatedCandidates, RootCause, compute_impact, prioritize_incidents_by_local_impact, to_incident


def _incident(*, incident_id: str, amount_minor: int, currency: str):
    return to_incident(
        CorrelatedCandidates(
            candidates=(
                {
                    "slice": {"country": "BR" if currency == "BRL" else "MX"},
                    "window": {"start": "2026-08-29T15:00:00Z", "end": "2026-08-29T15:05:00Z"},
                    "lost_approvals": 10,
                    "sample_size": 100,
                    "observed": 0.70,
                    "expected": 0.80,
                },
            ),
            correlation_id=f"corr_{incident_id}",
        ),
        compute_impact(
            CorrelatedCandidates(
                candidates=(
                    {"lost_approvals": 10},
                    {"lost_approvals": 4},
                ),
                correlation_id=f"corr_{incident_id}",
            ),
            {"eligible_attempts": 100, "amount_minor": amount_minor * 10, "currency": currency},
        ),
        RootCause(status="SUPPORTED", category="PROVIDER_DEGRADATION", confidence=0.9, confidence_factors={"test": 0.9}),
        incident_id=incident_id,
        title=incident_id,
        evidence=[
            {
                "evidence_id": f"evd_{incident_id}",
                "kind": "METRIC_SHIFT",
                "statement": "Test evidence.",
                "source_ref": "test://incident-priority",
            }
        ],
        recommendations=[],
    )


def test_compute_impact_uses_max_lost_approvals_without_double_counting():
    impact = compute_impact(
        CorrelatedCandidates(candidates=({"lost_approvals": 10}, {"lost_approvals": 4}), correlation_id="corr_brl"),
        {"eligible_attempts": 100, "amount_minor": 1_200_000, "currency": "BRL"},
    )

    assert impact.amount_minor == 120_000
    assert impact.currency == "BRL"


def test_priority_buckets_rank_local_gmv_without_implicit_fx_conversion():
    brl_lower = _incident(incident_id="inc_brl_lower", amount_minor=120_000, currency="BRL")
    brl_higher = _incident(incident_id="inc_brl_higher", amount_minor=240_000, currency="BRL")
    mxn = _incident(incident_id="inc_mxn", amount_minor=500_000, currency="MXN")

    buckets = prioritize_incidents_by_local_impact([brl_lower, mxn, brl_higher])

    assert list(buckets) == ["BRL", "MXN"]
    assert [incident.incident_id for incident in buckets["BRL"]] == ["inc_brl_higher", "inc_brl_lower"]
    assert [incident.incident_id for incident in buckets["MXN"]] == ["inc_mxn"]


def test_compute_impact_rejects_windows_without_eligible_attempts():
    with pytest.raises(ValueError, match="eligible_attempts"):
        compute_impact(
            CorrelatedCandidates(candidates=({"lost_approvals": 1},), correlation_id="corr_empty"),
            {"eligible_attempts": 0, "amount_minor": 0, "currency": "BRL"},
        )
