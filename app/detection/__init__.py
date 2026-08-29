"""CMP-DET-001 seasonal anomaly detection."""

from .detector import (
    DETECTOR_VERSION,
    approval_rate_signal,
    build_seasonal_baseline,
    detect_candidates,
    latency_p95_signal,
    timeout_rate_signal,
    to_anomaly_candidate,
)
from .models import AnomalyCandidate, DetectionSignal, SeasonalBaseline

__all__ = [
    "AnomalyCandidate",
    "DETECTOR_VERSION",
    "DetectionSignal",
    "SeasonalBaseline",
    "approval_rate_signal",
    "build_seasonal_baseline",
    "detect_candidates",
    "latency_p95_signal",
    "timeout_rate_signal",
    "to_anomaly_candidate",
]
