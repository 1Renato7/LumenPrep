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
from app.api.transactions import BatchRequest, TransactionInput, _create_batch
from app.worker.transaction_worker import run_batch_to_completion
from uuid import uuid4

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


@router.post("/demo/scenarios/{scenario_id}/inject-worker", status_code=202)
def inject_scenario_through_worker(scenario_id: str) -> dict[str, Any]:
    """Evaluation-only scenario path that exercises the public batch worker."""
    if not settings.demo_mode:
        raise HTTPException(status_code=403, detail="DEMO_MODE_REQUIRED")
    payload = _load_scenario(scenario_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="SCENARIO_NOT_FOUND")
    scenario = _scenario_contract.parse(payload)
    provider = scenario.filters.get("provider_id", ("stripe",))[0]
    country = scenario.filters.get("country", ("BR",))[0]
    currency = {"BR": "BRL", "MX": "MXN", "CO": "COP"}.get(country, "BRL")
    transactions = [
        TransactionInput(
            client_reference=f"scenario-worker-{scenario_id}-{index}", merchant_id="merchant_br_01",
            occurred_at="2026-08-29T12:00:00Z",
            provider_id=provider, issuer_bank="bank_br_a", country=country, currency=currency,
            amount_minor=12990, payment_method_category="CARD", card_brand="MASTERCARD",
            card_type="CREDIT", provider_connection_id=f"conn_{country.lower()}_primary", channel="WEB",
            scenario_effects={key: float(value) for key, value in scenario.effects.items() if isinstance(value, (int, float))},
        )
        for index in range(50)
    ]
    response = _create_batch(BatchRequest(schema_version="1.0", idempotency_key=f"scenario-{uuid4().hex}", transactions=transactions))
    run_batch_to_completion(response["batch_id"])
    return {"status": "ACCEPTED", "scenario_id": scenario_id, "source": "transaction_worker", **response}


class BackgroundTrafficRequest(BaseModel):
    count: int = Field(ge=1, le=100)
    seed: int | None = Field(default=None, ge=0)


class BaselineTrafficRequest(BaseModel):
    window_count: int = Field(default=12, ge=2, le=48)
    payments_per_window: int = Field(default=60, ge=12, le=200)


@router.post("/demo/baseline-traffic", status_code=202)
def seed_baseline_traffic(request: BaselineTrafficRequest) -> dict[str, Any]:
    """CTR-DEMO-001 v1: seed synthetic history through the live stream only."""
    if not settings.demo_mode:
        raise HTTPException(status_code=403, detail="DEMO_MODE_REQUIRED")
    result = _get_controller().seed_baseline_history(
        window_count=request.window_count,
        payments_per_window=request.payments_per_window,
    )
    return {
        "status": "ACCEPTED",
        "source": "live_stream",
        "window_count": result.window_count,
        "payments_requested": result.payments_requested,
        "events_published": result.events_published,
        "first_window_start": result.first_window_start,
        "last_window_end": result.last_window_end,
    }


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
