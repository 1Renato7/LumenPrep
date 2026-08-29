"""TASK-API-003: local demo scenario injection boundary.

TODO(TASK-DATA-006): replace fixture acknowledgement with the data owner's
public injection function once its package and signature are delivered.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from app.config import settings

router = APIRouter()
_SCENARIOS = Path(__file__).resolve().parents[2] / "contracts" / "fixtures"


def _load_scenario(scenario_id: str) -> dict[str, Any] | None:
    names = (f"{scenario_id}.json", f"{scenario_id.replace('_', '-')}.json")
    for name in names:
        path = _SCENARIOS / name
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


@router.post("/demo/scenarios/{scenario_id}/inject", status_code=202)
def inject_scenario(scenario_id: str) -> dict[str, Any]:
    """Accept only known synthetic scenarios while DEMO_MODE is enabled."""
    if not settings.demo_mode:
        raise HTTPException(status_code=403, detail="DEMO_MODE_REQUIRED")
    scenario = _load_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="SCENARIO_NOT_FOUND")
    return {
        "status": "ACCEPTED",
        "scenario_id": scenario["scenario_id"],
        "correlation_id": f"demo:{scenario['scenario_id']}",
        "source": "fixture_fallback",
        "integration_pending": "TASK-DATA-006",
    }
