"""Typed values internal to CMP-DET-001."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


MetricName = Literal["APPROVAL_RATE", "PAYMENT_CONVERSION", "LATENCY_P95", "TIMEOUT_RATE"]


class SeasonalBaseline(BaseModel):
    """Seasonal expectation calculated only from prior windows of one slice."""

    approval_rate: float
    payment_conversion: float = 0.0
    latency_p95_ms: float
    latency_p95_mad: float
    timeout_rate: float
    sample_size: int
    window_count: int
    pooling_level: Literal["weekday_hour", "hour", "global"]


class DetectionSignal(BaseModel):
    """A metric deviation that passed its detector-specific significance test."""

    metric: MetricName
    observed: float
    expected: float
    statistical_strength: float


class AnomalyCandidate(BaseModel):
    """CTR-DET-001 v1 payload. It deliberately contains no root-cause claim."""

    schema_version: Literal["1.0", "2.0"] = "1.0"
    candidate_id: str
    window: dict[str, str]
    slice: dict[str, str]
    metric: MetricName
    observed: float
    expected: float
    sample_size: int
    effect_absolute: float
    effect_relative: float
    statistical_strength: float
    lost_approvals: float
    estimated_lost_conversions: float = 0.0
    loss_coverage: float
    temporal_consistency: float
    data_quality: float
    evidence_refs: list[str]
    detector_version: str
    correlation_id: str
