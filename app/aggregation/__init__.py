"""CMP-AGG-001 — expõe get_current_metrics, WindowMetrics. TASK-AGG-001..002."""

from pydantic import BaseModel


class WindowMetrics(BaseModel):
    schema_version: str = "1.0"
    window_start: str
    window_end: str
    dimensions: dict[str, str]
    eligible_attempts: int
    approved_attempts: int
    unique_payments: int
    approved_payments: int
    amount_minor: int
    currency: str
    approval_rate: float
    payment_conversion: float
    latency_p50_ms: float
    latency_p95_ms: float
    timeout_rate: float
    decline_counts: dict[str, int]
    decline_profile: dict[str, int] = {}
    data_quality: float
    window_revision: int
    correlation_id: str


from .windows import compute_windows  # noqa: E402  (depende de WindowMetrics acima)


def get_current_metrics(dimensions: dict[str, str] | None = None) -> list[WindowMetrics]:
    from app.ingestion.storage import get_connection

    windows = compute_windows(get_connection())
    if dimensions:
        # Public callers asking for a slice expect one aggregation level, not
        # every descendant in the internal causal cube.
        windows = [
            w for w in windows
            if {key: value for key, value in w.dimensions.items() if key != "currency"} == dimensions
        ]
    return windows
