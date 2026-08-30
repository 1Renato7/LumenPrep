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
