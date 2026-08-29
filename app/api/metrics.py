"""TASK-API-001: read current metrics through the aggregation public seam."""

from fastapi import APIRouter

from app.aggregation import get_current_metrics

router = APIRouter()


@router.get("/metrics/current")
def metrics_current() -> list[dict[str, object]]:
    """Return CTR-AGG-001 records unchanged from the aggregation boundary."""
    return [metric.model_dump() for metric in get_current_metrics()]
