"""TASK-API-003: local demo scenario injection boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.simulation import LiveStreamController, ScenarioV1Contract, load_generator_config
from app.simulation.scenario_contract import ScenarioContractError
from app.streaming import get_transaction_server

router = APIRouter()
_SCENARIOS = Path(__file__).resolve().parents[2] / "contracts" / "fixtures"
_GENERATOR_CONFIG = Path(__file__).resolve().parents[2] / "config" / "generator" / "v1" / "default.json"
_SCENARIO_SCHEMA = Path(__file__).resolve().parents[2] / "contracts" / "v1" / "scenario.schema.json"

_controller: LiveStreamController | None = None
_scenario_contract = ScenarioV1Contract(_SCENARIO_SCHEMA)


def _get_controller() -> LiveStreamController:
    global _controller
    if _controller is None:
        _controller = LiveStreamController(load_generator_config(_GENERATOR_CONFIG), get_transaction_server())
    return _controller


def _load_scenario(scenario_id: str) -> dict[str, Any] | None:
    names = (f"{scenario_id}.json", f"{scenario_id.replace('_', '-')}.json")
    for name in names:
        path = _SCENARIOS / name
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


@router.post("/demo/scenarios/{scenario_id}/inject", status_code=202)
def inject_scenario(scenario_id: str) -> dict[str, Any]:
    """Accept only known synthetic scenarios while DEMO_MODE is enabled.

    Injeta de verdade: gera trafego via app.simulation (TASK-DATA-006),
    aplica os effects de CTR-SCN-001 nas tentativas que casam os filters,
    e ingere via app.ingestion.ingest_event real — reflete em
    /metrics/current e nos incidentes na sequencia.
    """
    if not settings.demo_mode:
        raise HTTPException(status_code=403, detail="DEMO_MODE_REQUIRED")
    payload = _load_scenario(scenario_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="SCENARIO_NOT_FOUND")

    try:
        scenario = _scenario_contract.parse(payload)
    except ScenarioContractError as error:
        raise HTTPException(status_code=422, detail=f"SCENARIO_CONTRACT_INVALID: {error}") from error
    result = _get_controller().inject_scenario(scenario)

    return {
        "status": "ACCEPTED",
        "scenario_id": result.scenario_id,
        "correlation_id": result.correlation_id,
        "source": "live_stream",
        "matched_attempts": result.matched_attempts,
        "events_published": result.events_published,
    }


class BackgroundTrafficRequest(BaseModel):
    count: int = Field(ge=1, le=100)
    seed: int | None = Field(default=None, ge=0)


@router.post("/demo/background-traffic", status_code=202)
def emit_background_traffic(request: BackgroundTrafficRequest) -> dict[str, Any]:
    """TASK-DATA-009: demo-only trigger for background traffic through the batch API."""
    if not settings.demo_mode:
        raise HTTPException(status_code=403, detail="DEMO_MODE_REQUIRED")
    try:
        # Import lazily because background_traffic consumes the public batch API.
        # Importing it while app.api assembles its routers would form a cycle.
        from app.simulation.background_traffic import submit_background_batch

        return submit_background_batch(request.count, seed=request.seed)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
