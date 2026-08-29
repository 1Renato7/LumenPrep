"""TASK-API-001: local dependency health without accessing storage directly."""

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, object]:
    """Expose configuration state only; dependency clients own their own probes."""
    return {
        "status": "ok",
        "dependencies": {
            "duckdb": "managed_by_ingestion_aggregation",
            "neo4j": "not_configured" if not settings.neo4j_uri else "configured",
            "openai": "not_configured" if not settings.openai_api_key else "configured",
        },
    }
