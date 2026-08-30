"""Build the immutable CTR-AGT-001 EvidencePack from a persisted Incident.

Everything here is a projection of facts the deterministic engine already
computed.  The builder never queries a provider, never recomputes a metric and
never derives a cause; if a fact is missing it is recorded as a limitation
rather than estimated.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.incidents import Incident

from .models import (
    CausalAlternative,
    EngineRootCause,
    EvidenceItem,
    EvidencePack,
    ImpactSummary,
    ObservationWindow,
    RefusalCodeSummary,
    sealed,
)

ENGINE_VERSION = "cube-rca-v2"


def build_evidence_pack(
    incident: Incident | Mapping[str, Any],
    *,
    decline_profile: Mapping[str, int] | None = None,
    refusal_code_summaries: list[Mapping[str, Any]] | None = None,
    engine_version: str = ENGINE_VERSION,
) -> EvidencePack:
    """Project one persisted Incident into the agent's only view of the world."""
    payload = incident.model_dump(mode="json") if isinstance(incident, Incident) else dict(incident)
    metrics = payload.get("metrics") or {}
    root_cause = payload["root_cause"]
    evidence = [EvidenceItem.model_validate(item) for item in payload.get("evidence", [])]

    limitations = list(payload.get("limitations", []))
    if decline_profile is None:
        limitations.append(
            "The decline profile of the observed window was not available to the agent; "
            "decline-based reasoning is out of scope for this suggestion."
        )

    summaries = [RefusalCodeSummary.model_validate(item) for item in (refusal_code_summaries or [])]
    code_evidence = [EvidenceItem(
        evidence_id=item.evidence_id, kind="REFUSAL_CODE_SUMMARY",
        statement=(f"{item.transaction_count} transaction(s) resolved as code {item.response_code} "
                   f"({item.normalized_code}) for {item.provider_id}/{item.issuer_bank}/{item.card_brand}: {item.reason}."),
        source_ref=f"refusal-catalog://{item.source}/{item.mapping_version}",
    ) for item in summaries]
    pack = EvidencePack(
        incident_id=str(payload["incident_id"]),
        correlation_id=str(payload["correlation_id"]),
        scope={str(key): [str(item) for item in values] for key, values in payload.get("scope", {}).items()},
        window=ObservationWindow(
            start=str(payload["estimated_started_at"]),
            end=str(payload["detected_at"]),
        ),
        approval_rate_observed=_optional_float(metrics.get("approval_rate_observed")),
        approval_rate_expected=_optional_float(metrics.get("approval_rate_expected")),
        eligible_attempts=_non_negative_int(metrics.get("eligible_attempts")),
        lost_approvals=_non_negative_int(metrics.get("lost_approvals")),
        # ``Impact`` carries optional uncertainty bounds the pack deliberately
        # drops, so the four required fields are copied explicitly.
        impact=ImpactSummary(
            metric=str(payload["impact"]["metric"]),
            method=str(payload["impact"]["method"]),
            amount_minor=int(payload["impact"]["amount_minor"]),
            currency=str(payload["impact"]["currency"]),
        ),
        detector_evidence=[*evidence, *code_evidence],
        rca_alternatives=[
            CausalAlternative(category=str(item["category"]), confidence=float(item["confidence"]))
            for item in root_cause.get("alternatives", [])
        ],
        decline_profile={str(code): int(count) for code, count in (decline_profile or {}).items()},
        refusal_code_summaries=summaries,
        limitations=limitations,
        # The agent may cite only what already exists. Retrieval widens this set
        # later with precedent evidence IDs; it never widens itself.
        authorized_evidence_ids=sorted({item.evidence_id for item in [*evidence, *code_evidence]}),
        root_cause=EngineRootCause(
            status=str(root_cause["status"]),
            category=root_cause.get("category"),
            confidence=float(root_cause.get("confidence", 0.0)),
        ),
        engine_version=engine_version,
    )
    return sealed(pack)


def _optional_float(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _non_negative_int(value: object) -> int:
    if value is None or isinstance(value, bool):
        return 0
    try:
        return max(0, int(round(float(value))))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0
