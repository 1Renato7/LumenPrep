from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router as api_router
from app.streaming import IngestionListenerWorker, get_ingestion_listener


@asynccontextmanager
async def transaction_listener_lifespan(_: FastAPI):
    worker = IngestionListenerWorker(get_ingestion_listener())
    worker.start()
    try:
        yield
    finally:
        worker.stop()


app = FastAPI(title="Lumen Read API", lifespan=transaction_listener_lifespan)
app.include_router(api_router)
