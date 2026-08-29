"""TASK-API-002: typed incident read endpoints.

TODO(TASK-RCA-002): replace the fixture repository with RCA-produced Incident
records when real correlator output exists.
TODO(TASK-EXP-003): bind confirmed public functions from app.memory and
app.explanation; their signatures remain unconfirmed by their owner.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter()
_FIXTURES = Path(__file__).resolve().parents[2] / "contracts" / "fixtures"


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


def _fixture_memory_and_explanation(incident_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if incident_id == "inc_current_mastercard_001":
        return _fixture("similar-incidents.json"), _fixture("explanation-bundle.json")
    if incident_id == "inc_current_mastercard_uncertain_002":
        return _fixture("similar-incidents-inconclusive-current.json"), _fixture("explanation-bundle-inconclusive-with-precedent.json")
    if incident_id == "inc_new_provider_country_001":
        return _fixture("similar-incidents-empty.json"), _fixture("explanation-bundle-no-precedent.json")
    raise KeyError(incident_id)


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
def list_incidents() -> list[dict[str, Any]]:
    """List current records. Fixture-only until TASK-RCA-002 lands."""
    return list(_fixture_records().values())


@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str) -> dict[str, Any]:
    incident = _fixture_records().get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="INCIDENT_NOT_FOUND")
    memory, explanation = _fixture_memory_and_explanation(incident_id)
    return build_incident_response(incident, memory, explanation)
