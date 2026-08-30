"""TASK-API-002: typed incident read endpoints.

TODO(TASK-RCA-002): replace the fixture repository with RCA-produced Incident
records when real correlator output exists.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, model_validator

from app.agent import DiagnosticSuggestionRepository
from app.config import settings
from app.explanation import (
    GroundedExplainer,
    TransactionGrounding,
    resolve_transaction_grounding_from_api_responses,
)
from app.incidents import DuckDBIncidentRepository, ReviewIdConflictError
from app.ingestion.storage import transaction_record_for_grounding
from app.memory import (
    Incident,
    IncidentMemoryService,
    InMemoryIncidentRepository,
    Neo4jIncidentRepository,
)
from app.memory.promotion import IncidentPromoter, PromotionReview
from app.memory.repository import IncidentMemoryRepository
from app.memory.seed import seed_mastercard_d2

router = APIRouter()
_FIXTURES = Path(__file__).resolve().parents[2] / "contracts" / "fixtures"
_neo4j_driver: Any | None = None
_neo4j_driver_failed = False


class HumanReviewRequest(BaseModel):
    """CTR-HRV-001 v1 — a reviewer, not an agent, owns this decision."""

    schema_version: Literal["1.0"] = "1.0"
    review_id: str = Field(min_length=8, max_length=120)
    reviewer_id: str = Field(min_length=1, max_length=120)
    decision: Literal["APPROVED", "REJECTED"]
    reason: str = Field(min_length=3, max_length=4_000)
    confirmed_cause: str | None = Field(default=None, max_length=160)
    playbook_id: str | None = Field(default=None, max_length=160)

    @model_validator(mode="after")
    def approved_reviews_require_a_cause_and_playbook(self) -> "HumanReviewRequest":
        if self.decision == "APPROVED" and (not self.confirmed_cause or not self.playbook_id):
            raise ValueError("APPROVED requires confirmed_cause and playbook_id")
        if self.decision == "REJECTED" and (self.confirmed_cause is not None or self.playbook_id is not None):
            raise ValueError("REJECTED must not include confirmed_cause or playbook_id")
        return self


def _neo4j_driver_instance() -> Any | None:
    """Build the Neo4j driver once; a construction failure disables the driver for the process."""
    global _neo4j_driver, _neo4j_driver_failed
    if _neo4j_driver is not None or _neo4j_driver_failed:
        return _neo4j_driver
    try:
        from neo4j import GraphDatabase

        _neo4j_driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    except Exception:
        _neo4j_driver_failed = True
    return _neo4j_driver


def _memory_repository() -> IncidentMemoryRepository | None:
    """Neo4j primary when configured and reachable; None makes fallback the sole repository."""
    if not settings.neo4j_uri:
        return None
    driver = _neo4j_driver_instance()
    if driver is None:
        return None
    return Neo4jIncidentRepository(
        driver,
        database=settings.neo4j_database,
        include_evaluation=False,
    )


def _fixture(name: str) -> dict[str, Any]:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


def _with_incident_id(payload: dict[str, Any], incident_id: str) -> dict[str, Any]:
    result = deepcopy(payload)
    result["incident_id"] = incident_id
    return result


def _fixture_records() -> dict[str, dict[str, Any]]:
    supported = _fixture("incident-mastercard-recurrence.json")
    inconclusive = _fixture("incident-inconclusive-with-precedent.json")
    no_precedent_explanation = _fixture("explanation-bundle-no-precedent.json")
    no_precedent = {
        "schema_version": "1.0",
        "incident_id": "inc_new_provider_country_001",
        "state": "SUPPORTED",
        "detected_at": supported["detected_at"],
        "estimated_started_at": supported["estimated_started_at"],
        "title": "Approval-rate drop for provider_new in Brazil",
        "scope": {"provider_id": ["provider_new"], "country": ["BR"]},
        "metrics": {
            "approval_rate_observed": 0.58,
            "approval_rate_expected": 0.82,
            "lost_approvals": 0,
        },
        "root_cause": {
            "status": "SUPPORTED",
            "category": "PROVIDER_DEGRADATION",
            "confidence": 0.88,
            "confidence_factors": {"fixture_fallback": 0.88},
            "alternatives": [],
        },
        "impact": {
            "metric": "GMV_AT_RISK",
            "amount_minor": 1840000,
            "currency": "BRL",
            "method": "EXPECTED_APPROVAL_SHORTFALL",
        },
        "evidence": [
            {
                "evidence_id": evidence_id,
                "kind": "FIXTURE_FALLBACK",
                "statement": "Derived from explanation-bundle-no-precedent fixture.",
                "source_ref": "fixture://explanation-bundle-no-precedent.json",
            }
            for evidence_id in no_precedent_explanation["evidence_ids"]
        ],
        "recommendations": [
            {
                "playbook_id": no_precedent_explanation["playbook_id"],
                "action": no_precedent_explanation["recommended_action"],
                "recommendation_class": "INVESTIGATE",
                "execution": "HUMAN_ONLY",
                "rationale_evidence_ids": no_precedent_explanation["evidence_ids"],
            }
        ],
        "limitations": no_precedent_explanation["limitations"],
        "correlation_id": "corr_new_provider_country_001",
    }
    return {
        supported["incident_id"]: supported,
        inconclusive["incident_id"]: inconclusive,
        no_precedent["incident_id"]: no_precedent,
    }


def _memory_and_explanation(incident_payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Enrich a current Incident without treating historical memory as its cause."""
    incident = Incident.from_contract(incident_payload)
    fallback = InMemoryIncidentRepository()
    seed_mastercard_d2(fallback, now=incident.detected_at)
    primary = _memory_repository()
    service = IncidentMemoryService(primary, fallback=fallback) if primary else IncidentMemoryService(fallback)
    memory = service.retrieve(incident)
    explanation = GroundedExplainer(()).explain(incident, memory)
    return memory.to_contract(), explanation.to_contract()


def _incident_records() -> dict[str, dict[str, Any]]:
    """Use fixtures only in the explicitly selected offline demo adapter."""
    if settings.demo_mode:
        return _fixture_records()
    return {
        incident.incident_id: incident.model_dump(mode="json")
        for incident in DuckDBIncidentRepository().list()
    }


def build_incident_response(incident: dict[str, Any], memory: dict[str, Any], explanation: dict[str, Any]) -> dict[str, Any]:
    """Compose CTR-API-001 without conflating current diagnosis and memory."""
    if memory["memory_status"] == "MATCH_FOUND" and not memory["matches"]:
        raise ValueError("MATCH_FOUND requires at least one memory match")
    if memory["memory_status"] != "MATCH_FOUND" and memory["matches"]:
        raise ValueError("only MATCH_FOUND may expose memory matches")
    serialized_incident = deepcopy(incident)
    serialized_incident.pop("memory_matches", None)
    if explanation["incident_id"] != serialized_incident["incident_id"]:
        explanation = _with_incident_id(explanation, serialized_incident["incident_id"])
    if memory["query_incident_id"] != serialized_incident["incident_id"]:
        memory = deepcopy(memory)
        memory["query_incident_id"] = serialized_incident["incident_id"]
    return {"incident": serialized_incident, "memory": memory, "explanation": explanation}


def _grounding_for_transaction(
    transaction_id: str,
) -> tuple[dict[str, dict[str, Any]], TransactionGrounding] | None:
    """Build candidate detail responses, then let the trace resolver authorize them."""
    transaction_record = transaction_record_for_grounding(transaction_id)
    if transaction_record is None:
        return None

    classification = transaction_record.get("classification")
    related_ids = classification.get("related_incident_ids", []) if isinstance(classification, dict) else []
    records = _incident_records()
    candidate_responses: dict[str, dict[str, Any]] = {}
    for incident_id in related_ids:
        if not isinstance(incident_id, str):
            continue
        incident = records.get(incident_id)
        if incident is None:
            continue
        memory, explanation = _memory_and_explanation(incident)
        candidate_responses[incident_id] = build_incident_response(incident, memory, explanation)

    grounding = resolve_transaction_grounding_from_api_responses(
        transaction_id,
        [transaction_record],
        candidate_responses,
    )
    return candidate_responses, grounding


def _grounding_detail_contract(
    transaction_id: str,
    candidate_responses: dict[str, dict[str, Any]],
    grounding: TransactionGrounding,
) -> dict[str, Any]:
    """Serialize CTR-TDI-001 without changing the homogeneous incidents list."""
    incidents = []
    for link in grounding.incident_links:
        response = candidate_responses[link.incident_id]
        incidents.append(
            {
                "incident": response["incident"],
                "memory": response["memory"],
                "explanation": response["explanation"],
                "evidence_ids": list(link.evidence_ids),
                "limitations": list(link.limitations),
            }
        )
    return {
        "schema_version": "1.0",
        "transaction_id": transaction_id,
        "status": grounding.status,
        "incidents": incidents,
        "rejected_incident_ids": list(grounding.rejected_incident_ids),
        "limitations": list(grounding.limitations),
    }


@router.get("/incidents")
def list_incidents(transaction_id: str | None = Query(default=None, min_length=1)) -> list[dict[str, Any]]:
    """List records; transaction filtering exposes only evidence-authorized Incidents."""
    records = _incident_records()
    if transaction_id is None:
        return list(records.values())

    resolved = _grounding_for_transaction(transaction_id)
    if resolved is None:
        # An unknown transaction and one without a correlated Incident both have no
        # authorized Incident to expose.  The public collection contract therefore
        # remains an empty list instead of manufacturing an error or a record.
        return []
    candidate_responses, grounding = resolved
    return [candidate_responses[incident_id]["incident"] for incident_id in grounding.incident_ids]


@router.get("/transactions/{transaction_id}/incidents")
def get_transaction_incidents(transaction_id: str) -> dict[str, Any]:
    """Return CTR-TDI-001, the explicit grounded detail for one transaction."""
    resolved = _grounding_for_transaction(transaction_id)
    if resolved is None:
        raise HTTPException(status_code=404, detail="TRANSACTION_NOT_FOUND")
    candidate_responses, grounding = resolved
    return _grounding_detail_contract(transaction_id, candidate_responses, grounding)


@router.get("/incidents/{incident_id}/suggestion")
def get_incident_suggestion(incident_id: str) -> dict[str, Any]:
    """Return CTR-AGT-003, the agent hypothesis, as a resource of its own.

    Keeping it off the Incident payload preserves frozen ``CTR-INC-001 v1`` and
    makes the separation legible to a consumer: an absent suggestion is a typed
    404, never an empty hypothesis attached to a real diagnosis.
    """
    if incident_id not in _incident_records():
        raise HTTPException(status_code=404, detail="INCIDENT_NOT_FOUND")
    suggestion = DiagnosticSuggestionRepository().latest_for_incident(incident_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="SUGGESTION_NOT_AVAILABLE")
    return suggestion.model_dump(mode="json")


@router.get("/notifications")
def list_notifications() -> dict[str, Any]:
    """Return persistent in-app notifications; the browser never derives unread state."""
    repository = DuckDBIncidentRepository()
    notifications = repository.notifications()
    records = _incident_records()
    values = [
        {**notification, "incident": records.get(notification["incident_id"])}
        for notification in notifications
        if notification["incident_id"] in records
    ]
    return {"notifications": values, "unread_count": sum(item["read_at"] is None for item in values)}


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str) -> dict[str, Any]:
    if not DuckDBIncidentRepository().mark_notification_read(notification_id):
        raise HTTPException(status_code=404, detail="NOTIFICATION_NOT_FOUND")
    return {"notification_id": notification_id, "read": True}


@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str) -> dict[str, Any]:
    incident = _incident_records().get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="INCIDENT_NOT_FOUND")
    memory, explanation = _memory_and_explanation(incident)
    return build_incident_response(incident, memory, explanation)


@router.post("/incidents/{incident_id}/review", status_code=201)
def review_incident(incident_id: str, request: HumanReviewRequest) -> dict[str, Any]:
    """Persist and mirror a human approval/rejection without agent authority."""
    repository = DuckDBIncidentRepository()
    current_contract = repository.get(incident_id)
    if current_contract is None:
        raise HTTPException(status_code=404, detail="INCIDENT_NOT_FOUND")
    try:
        review = repository.record_review(
            review_id=request.review_id, incident_id=incident_id, decision=request.decision,
            reviewer_id=request.reviewer_id, reason=request.reason,
            confirmed_cause=request.confirmed_cause, playbook_id=request.playbook_id,
        )
    except ReviewIdConflictError as error:
        raise HTTPException(status_code=409, detail="REVIEW_ID_CONFLICT") from error

    graph = _memory_repository()
    if graph is None:
        raise HTTPException(status_code=503, detail="GRAPH_MEMORY_UNAVAILABLE")
    current = Incident.from_contract(current_contract.model_dump(mode="json"))
    try:
        # Mirror the human rationale first. If promotion subsequently fails, a
        # retry has an audit trail but no unqualified historical precedent.
        graph.record_human_review(current, review)
        if request.decision == "APPROVED":
            decline_values = current_contract.metrics.get("decline_codes", [])
            decline_codes = tuple(str(value) for value in decline_values) if isinstance(decline_values, list) else ()
            temporal_shape = str(current_contract.metrics.get("temporal_shape") or current_contract.metrics.get("metric") or "OBSERVED_WINDOW")
            IncidentPromoter(graph).promote(current, PromotionReview(
                review_id=request.review_id, incident_id=incident_id, reviewer_id=request.reviewer_id,
                confirmed_cause=request.confirmed_cause or "", playbook_id=request.playbook_id or "",
                decline_codes=decline_codes, temporal_shape=temporal_shape,
                provenance="REAL_HUMAN_REVIEW",
            ))
    except Exception as error:
        raise HTTPException(status_code=503, detail="GRAPH_MEMORY_UNAVAILABLE") from error
    return {"schema_version": "1.0", "review": review, "promoted_to_memory": request.decision == "APPROVED"}
