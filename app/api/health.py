"""TASK-API-001: local dependency health without accessing storage directly."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.ingestion.storage import CONNECTION_LOCK, get_connection
from app.worker.transaction_worker import reconcile_stuck

router = APIRouter()


@router.get("/health")
def health(request: Request) -> JSONResponse:
    """Report whether the Railway deployment can serve durable transaction work."""
    try:
        with CONNECTION_LOCK:
            get_connection().execute("SELECT 1").fetchone()
        duckdb_status = "ready"
    except Exception as error:
        duckdb_status = f"unavailable:{type(error).__name__}"

    worker = getattr(request.app.state, "worker_reconciliation", None)
    if worker is None:
        try:
            worker = {"status": "ready", "records_reconciled": reconcile_stuck()}
        except Exception as error:
            worker = {"status": "unavailable", "error": type(error).__name__}
        request.app.state.worker_reconciliation = worker
    is_ready = duckdb_status == "ready" and worker["status"] == "ready"
    payload = {
        "status": "ok" if is_ready else "degraded",
        "dependencies": {
            "duckdb": duckdb_status,
            "worker": worker,
            "neo4j": "not_configured" if not settings.neo4j_uri else "configured",
            "openai": "not_configured" if not settings.openai_api_key else "configured",
        },
    }
    return JSONResponse(status_code=200 if is_ready else 503, content=payload)
