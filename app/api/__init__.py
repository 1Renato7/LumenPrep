"""CTR-API-001 v1 router assembly (TASK-API-001..003)."""

from fastapi import APIRouter

from app.api.demo import router as demo_router
from app.api.events import router as events_router
from app.api.health import router as health_router
from app.api.incidents import router as incidents_router
from app.api.metrics import router as metrics_router
from app.api.transactions import router as transactions_router

router = APIRouter()
# CTR-API-001 v3's servers block is https://.../v1 for every documented path — these
# three were still mounted at root, so contracts/v1/api.openapi.yaml's own /v1/health,
# /v1/metrics/current and /v1/incidents 404'd against the real app (verified directly).
# transactions_router already carries its own "/v1" prefix, so it is not repeated here.
router.include_router(health_router, prefix="/v1")
router.include_router(metrics_router, prefix="/v1")
router.include_router(incidents_router, prefix="/v1")
router.include_router(demo_router)
router.include_router(events_router)
router.include_router(transactions_router)
