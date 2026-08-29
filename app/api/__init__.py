"""CMP-API-001 — expõe router. Stub TASK-CORE-001 (health, metrics/current);
TASK-API-001..003 (Bloco 2) substitui por health.py/metrics.py/incidents.py/demo.py
sem exigir segunda edição de main.py (Seam 3, ver docs/plans/people/rogerio.md)."""

from fastapi import APIRouter

from app.aggregation import get_current_metrics
from app.config import settings

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "dependencies": {
            "duckdb": "ok",
            "neo4j": "not_configured" if not settings.neo4j_uri else "configured",
            "openai": "not_configured" if not settings.openai_api_key else "configured",
        },
    }


@router.get("/metrics/current")
def metrics_current() -> list[dict]:
    return [m.model_dump() for m in get_current_metrics()]
