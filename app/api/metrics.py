"""TASK-API-001: read current metrics through the aggregation public seam."""

from fastapi import APIRouter

from app.aggregation import get_current_metrics

router = APIRouter()


@router.get("/metrics/current")
def metrics_current() -> list[dict[str, object]]:
    """Return only root rollups; detailed cube slices stay internal to RCA."""
    return [
        metric.model_dump()
        for metric in get_current_metrics()
        if set(metric.dimensions) == {"currency"}
    ]
