from app.incidents import correlate_candidates


def _candidate(*, candidate_id: str, slice_values: dict[str, str], metric: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "correlation_id": "corr_simultaneous",
        "slice": slice_values,
        "metric": metric,
        "window": {"start": "2026-08-29T14:00:00Z", "end": "2026-08-29T14:05:00Z"},
        "lost_approvals": 10,
        "statistical_strength": 0.9,
        "loss_coverage": 0.8,
    }


def test_same_causal_slice_clusters_multiple_metrics_into_one_incident():
    groups = correlate_candidates(
        [
            _candidate(
                candidate_id="provider-approval",
                slice_values={"provider_id": "provider_alpha", "country": "BR"},
                metric="APPROVAL_RATE",
            ),
            _candidate(
                candidate_id="provider-latency",
                slice_values={"provider_id": "provider_alpha", "country": "BR"},
                metric="LATENCY_P95",
            ),
        ]
    )

    assert len(groups) == 1
    assert [candidate["candidate_id"] for candidate in groups[0].candidates] == [
        "provider-approval",
        "provider-latency",
    ]


def test_provider_br_and_issuer_mx_remain_independent_incidents():
    groups = correlate_candidates(
        [
            _candidate(
                candidate_id="provider-br",
                slice_values={"provider_id": "provider_alpha", "country": "BR"},
                metric="APPROVAL_RATE",
            ),
            _candidate(
                candidate_id="issuer-mx",
                slice_values={"issuer_bank": "bank_mx_a", "country": "MX"},
                metric="APPROVAL_RATE",
            ),
        ]
    )

    assert len(groups) == 2
    assert [{candidate["candidate_id"] for candidate in group.candidates} for group in groups] == [
        {"provider-br"},
        {"issuer-mx"},
    ]


def test_shared_country_alone_does_not_merge_distinct_causal_fingerprints():
    groups = correlate_candidates(
        [
            _candidate(
                candidate_id="provider-br",
                slice_values={"provider_id": "provider_alpha", "country": "BR"},
                metric="APPROVAL_RATE",
            ),
            _candidate(
                candidate_id="issuer-br",
                slice_values={"issuer_bank": "bank_br_a", "country": "BR"},
                metric="APPROVAL_RATE",
            ),
        ]
    )

    assert len(groups) == 2
