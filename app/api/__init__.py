"""CTR-API-001 v1 router assembly (TASK-API-001..003)."""

from fastapi import APIRouter

from app.api.demo import router as demo_router
from app.api.health import router as health_router
from app.api.incidents import router as incidents_router
from app.api.metrics import router as metrics_router

router = APIRouter()
router.include_router(health_router)
router.include_router(metrics_router)
router.include_router(incidents_router)
router.include_router(demo_router)
