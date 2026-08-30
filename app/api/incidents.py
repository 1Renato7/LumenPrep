"""TASK-API-002: typed incident read endpoints.

TODO(TASK-RCA-002): replace the fixture repository with RCA-produced Incident
records when real correlator output exists.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.explanation import GroundedExplainer
from app.ingestion.storage import related_incident_ids_for_transaction
from app.memory import (
    Incident,
    IncidentMemoryService,
    InMemoryIncidentRepository,
    Neo4jIncidentRepository,
)
from app.memory.repository import IncidentMemoryRepository
from app.memory.seed import seed_mastercard_d2

router = APIRouter()
_FIXTURES = Path(__file__).resolve().parents[2] / "contracts" / "fixtures"
_REAL_ENRICHMENT_INCIDENT_IDS = frozenset(
    {"inc_current_mastercard_001", "inc_current_mastercard_uncertain_002"}
)

_neo4j_driver: Any | None = None
_neo4j_driver_failed = False


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
    return Neo4jIncidentRepository(driver)


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
    incident_id = str(incident_payload["incident_id"])
    if incident_id not in _REAL_ENRICHMENT_INCIDENT_IDS:
        if incident_id == "inc_new_provider_country_001":
            return _fixture("similar-incidents-empty.json"), _fixture("explanation-bundle-no-precedent.json")
        raise KeyError(incident_id)

    incident = Incident.from_contract(incident_payload)
    fallback = InMemoryIncidentRepository()
    seed_mastercard_d2(fallback, now=incident.detected_at)
    primary = _memory_repository()
    service = IncidentMemoryService(primary, fallback=fallback) if primary else IncidentMemoryService(fallback)
    memory = service.retrieve(incident)
    explanation = GroundedExplainer(()).explain(incident, memory)
    return memory.to_contract(), explanation.to_contract()


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


@router.get("/incidents")
def list_incidents(transaction_id: str | None = Query(default=None, min_length=1)) -> list[dict[str, Any]]:
    """List current records, optionally restricted to a transaction's authored links."""
    records = _fixture_records()
    if transaction_id is None:
        return list(records.values())

    related_ids = related_incident_ids_for_transaction(transaction_id)
    if not related_ids:
        # An unknown transaction and one without a correlated Incident both have no
        # authorized Incident to expose.  The public collection contract therefore
        # remains an empty list instead of manufacturing an error or a record.
        return []
    return [records[incident_id] for incident_id in related_ids if incident_id in records]


@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str) -> dict[str, Any]:
    incident = _fixture_records().get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="INCIDENT_NOT_FOUND")
    memory, explanation = _memory_and_explanation(incident)
    return build_incident_response(incident, memory, explanation)
