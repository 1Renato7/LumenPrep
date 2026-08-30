import pytest

from app.incidents import (
    CorrelatedCandidates,
    Impact,
    Incident,
    Recommendation,
    RootCause,
    RootCauseAlternative,
    to_incident,
)


def test_root_cause_serializes_alternatives_in_confidence_order():
    cause = RootCause(
        status="INCONCLUSIVE",
        category=None,
        confidence=0.42,
        confidence_factors={"coverage": 0.42},
        alternatives=[
            RootCauseAlternative(category="ISSUER_OUTAGE", confidence=0.31),
            RootCauseAlternative(category="PROVIDER_DEGRADATION", confidence=0.38),
        ],
    )

    assert cause.status == "INCONCLUSIVE"
    assert cause.category is None
    assert [alternative.category for alternative in cause.alternatives] == [
        "PROVIDER_DEGRADATION",
        "ISSUER_OUTAGE",
    ]


def test_recommendation_defaults_to_human_investigation():
    recommendation = Recommendation(
        playbook_id="PB-GENERIC-INVESTIGATION",
        action="Inspect the current evidence.",
        rationale_evidence_ids=["evd_current_rate"],
    )

    assert recommendation.recommendation_class == "INVESTIGATE"
    assert recommendation.execution == "HUMAN_ONLY"


def test_incident_serializer_preserves_inconclusive_cause_and_hypotheses():
    cause = RootCause(
        status="INCONCLUSIVE",
        category=None,
        confidence=0.42,
        confidence_factors={"coverage": 0.42},
        alternatives=[
            RootCauseAlternative(category="ISSUER_OUTAGE", confidence=0.31),
            RootCauseAlternative(category="PROVIDER_DEGRADATION", confidence=0.38),
        ],
    )
    incident = to_incident(
        CorrelatedCandidates(
            candidates=(
                {
                    "slice": {"country": "BR"},
                    "window": {"start": "2026-08-29T15:00:00Z", "end": "2026-08-29T15:05:00Z"},
                    "lost_approvals": 13,
                    "sample_size": 86,
                    "observed": 0.67,
                    "expected": 0.82,
                },
            ),
            correlation_id="corr_incident_serialization",
        ),
        Impact(amount_minor=194000, currency="BRL"),
        cause,
        incident_id="inc_serialization_001",
        title="Inconclusive fixture",
        evidence=[
            {
                "evidence_id": "evd_current_rate",
                "kind": "METRIC_SHIFT",
                "statement": "Current evidence remains inconclusive.",
                "source_ref": "test://incident-serialization",
            }
        ],
        recommendations=[
            {
                "playbook_id": "PB-GENERIC-INVESTIGATION",
                "action": "Inspect the current evidence.",
                "rationale_evidence_ids": ["evd_current_rate"],
            }
        ],
    )

    payload = incident.model_dump()
    assert payload["root_cause"]["status"] == "INCONCLUSIVE"
    assert payload["root_cause"]["category"] is None
    assert [alternative["category"] for alternative in payload["root_cause"]["alternatives"]] == [
        "PROVIDER_DEGRADATION",
        "ISSUER_OUTAGE",
    ]
    assert payload["recommendations"][0]["recommendation_class"] == "INVESTIGATE"
    assert payload["recommendations"][0]["execution"] == "HUMAN_ONLY"

    mismatched = {**payload, "state": "SUPPORTED"}
    with pytest.raises(ValueError, match="state must match root_cause.status"):
        Incident.model_validate(mismatched)


def _candidate(metric: str, *, observed: float, expected: float) -> dict:
    return {
        "candidate_id": f"det_{metric.lower()}",
        "window": {"start": "2026-08-03T10:00:00Z", "end": "2026-08-03T10:05:00Z"},
        "slice": {"provider_id": "adyen", "country": "BR"},
        "metric": metric,
        "observed": observed,
        "expected": expected,
        "sample_size": 40,
        "lost_approvals": 0,
        "correlation_id": "corr-metric-keys",
    }


def _serialize(candidate: dict) -> dict:
    incident = to_incident(
        CorrelatedCandidates((candidate,), "corr-metric-keys"),
        Impact(amount_minor=0, currency="BRL"),
        RootCause(status="INCONCLUSIVE", category=None, confidence=0.4, confidence_factors={}),
        incident_id="inc_metric_keys",
        title="Payment degradation",
        evidence=[],
        recommendations=[],
    )
    return incident.model_dump(mode="json")["metrics"]


def test_a_latency_candidate_is_not_published_as_an_approval_rate():
    """A p95 in milliseconds under approval_rate_* broke the 0..1 bound of CTR-AGT-001."""
    metrics = _serialize(_candidate("LATENCY_P95", observed=2533.3, expected=478.3))

    assert metrics["metric"] == "LATENCY_P95"
    assert metrics["provider_latency_p95_ms_observed"] == 2533.3
    assert metrics["provider_latency_p95_ms_expected"] == 478.3
    assert "approval_rate_observed" not in metrics
    assert "approval_rate_expected" not in metrics


def test_a_timeout_candidate_carries_timeout_keys():
    metrics = _serialize(_candidate("TIMEOUT_RATE", observed=0.31, expected=0.01))

    assert metrics["metric"] == "TIMEOUT_RATE"
    assert metrics["timeout_rate_observed"] == 0.31
    assert "approval_rate_observed" not in metrics


def test_an_approval_candidate_keeps_the_published_keys():
    metrics = _serialize(_candidate("APPROVAL_RATE", observed=0.43, expected=0.92))

    assert metrics["metric"] == "APPROVAL_RATE"
    assert metrics["approval_rate_observed"] == 0.43
    assert metrics["approval_rate_expected"] == 0.92
