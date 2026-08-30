from app.api import incidents
from app.api.incidents import HumanReviewRequest
from app.incidents import DuckDBIncidentRepository


class FakeGraph:
    def __init__(self):
        self.promoted = []
        self.reviews = []

    def upsert(self, incident):
        self.promoted.append(incident)

    def record_human_review(self, incident, review):
        self.reviews.append((incident, review))


def _incident_id() -> str:
    return "inc_current_mastercard_001"


def _request(*, decision: str) -> HumanReviewRequest:
    base = {
        "review_id": f"review-{decision.lower()}-001", "reviewer_id": "operator_01",
        "decision": decision, "reason": "Reviewed with the payment operations team.",
    }
    if decision == "APPROVED":
        base.update({"confirmed_cause": "ISSUER_OUTAGE", "playbook_id": "PB-ISSUER-INVESTIGATION"})
    return HumanReviewRequest.model_validate(base)


def _store_current_incident():
    payload = incidents._fixture_records()[_incident_id()]
    return DuckDBIncidentRepository().upsert(payload)


def test_approved_review_promotes_and_mirrors_reason(monkeypatch):
    _store_current_incident()
    graph = FakeGraph()
    monkeypatch.setattr(incidents, "_memory_repository", lambda: graph)

    response = incidents.review_incident(_incident_id(), _request(decision="APPROVED"))

    assert response["promoted_to_memory"] is True
    assert len(graph.promoted) == 1
    assert graph.reviews[0][1]["reason"] == "Reviewed with the payment operations team."
    assert graph.reviews[0][1]["decision"] == "APPROVED"


def test_rejected_review_is_audited_but_never_promoted(monkeypatch):
    _store_current_incident()
    graph = FakeGraph()
    monkeypatch.setattr(incidents, "_memory_repository", lambda: graph)

    response = incidents.review_incident(_incident_id(), _request(decision="REJECTED"))

    assert response["promoted_to_memory"] is False
    assert graph.promoted == []
    assert graph.reviews[0][1]["decision"] == "REJECTED"


def test_same_review_id_with_different_decision_is_conflict(monkeypatch):
    _store_current_incident()
    monkeypatch.setattr(incidents, "_memory_repository", lambda: FakeGraph())
    incidents.review_incident(_incident_id(), _request(decision="REJECTED"))
    changed = _request(decision="APPROVED").model_copy(update={"review_id": "review-rejected-001"})

    try:
        incidents.review_incident(_incident_id(), changed)
    except Exception as error:
        assert getattr(error, "status_code", None) == 409
        assert getattr(error, "detail", None) == "REVIEW_ID_CONFLICT"
    else:
        raise AssertionError("expected review id conflict")
