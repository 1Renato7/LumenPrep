from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.config import Settings, settings
from app.streaming import IngestionListenerWorker, get_ingestion_listener
from app.worker.transaction_worker import reconcile_stuck


@asynccontextmanager
async def _lifespan(app: FastAPI):
    try:
        # Startup must restore durable transaction state without waiting on a
        # remote model call. New request-driven work still generates suggestions.
        app.state.worker_reconciliation = {
            "status": "ready", "records_reconciled": reconcile_stuck(run_suggestions=False)
        }
    except Exception as error:
        # Do not pretend the lifecycle is ready when the durable worker cannot recover it.
        app.state.worker_reconciliation = {"status": "unavailable", "error": type(error).__name__}
    listener_worker = IngestionListenerWorker(get_ingestion_listener())
    listener_worker.start()
    try:
        yield
    finally:
        listener_worker.stop()


def create_app(config: Settings = settings) -> FastAPI:
    """Create the public API with an opt-in, exact-origin CORS policy."""
    application = FastAPI(title="Lumen Read API", lifespan=_lifespan)
    if origins := config.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list(origins),
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "Idempotency-Key"],
        )
    application.include_router(api_router)
    return application


app = create_app()
