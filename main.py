from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router as api_router
from app.worker.transaction_worker import reconcile_stuck


@asynccontextmanager
async def _lifespan(app: FastAPI):
    reconcile_stuck()  # a restart must not strand transactions mid-pipeline (TASK-TXN-WORKER-001)
    yield


app = FastAPI(title="Lumen Read API", lifespan=_lifespan)
app.include_router(api_router)
