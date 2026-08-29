"""CMP-AGG-001 — expõe get_current_metrics, WindowMetrics. Stub TASK-CORE-001; real impl TASK-AGG-001/002."""

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
    data_quality: float
    window_revision: int
    correlation_id: str


_STUB = WindowMetrics(
    window_start="2026-08-29T14:00:00Z",
    window_end="2026-08-29T14:05:00Z",
    dimensions={"provider_id": "stripe", "country": "BR"},
    eligible_attempts=492,
    approved_attempts=251,
    unique_payments=470,
    approved_payments=258,
    amount_minor=7342000,
    currency="BRL",
    approval_rate=0.5102,
    payment_conversion=0.5489,
    latency_p50_ms=1100,
    latency_p95_ms=4100,
    timeout_rate=0.28,
    decline_counts={"PROVIDER_TIMEOUT": 169, "PROVIDER_INTERNAL_ERROR": 72},
    data_quality=0.98,
    window_revision=1,
    correlation_id="corr_window_001",
)


def get_current_metrics(dimensions: dict[str, str] | None = None) -> list[WindowMetrics]:
    """Stub. Real: TASK-AGG-001/002, query DuckDB windows."""
    return [_STUB]
