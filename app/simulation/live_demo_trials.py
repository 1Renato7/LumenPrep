"""CTR-DEMO-002 v1: fixed, reversible live-demo trial inputs.

The module owns only synthetic facts and calls the durable batch boundary; it
never inserts rows or Incidents directly.  It is intentionally small so the
whole feature can be disabled by one server-side flag or reverted cleanly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from app.api.transactions import BatchRequest, TransactionInput, _create_batch
from app.incidents import Incident, RootCause, RootCauseAlternative
from app.worker.transaction_worker import run_batch_to_completion

TrialId = Literal["deterministic", "graph_enriched"]
TrialFlow = Literal["DETERMINISTIC", "GRAPH_ENRICHED"]

_TRIAL_COUNT = 25
_TRIAL_SUCCESS_COUNT = 5
_BASELINE_COUNT = 12
_SECONDARY_FAILURE_INDEXES = frozenset({3, 4, 8, 9, 13, 14, 19, 24})
# A single 12-item healthy window is the smallest deterministic reference that
# clears the detector's low-sample guard. Keeping it small makes the live demo
# responsive and deliberately avoids the separate conversion detector, so each
# fixed trial exercises one approval-rate Incident.
_BASELINE_WINDOWS = 1
_BASE_TIME = datetime(2026, 8, 29, 14, 0, tzinfo=timezone.utc)
_GRAPH_MERCHANTS = (
    "merchant_br_01",
    "merchant_br_aurora",
    "merchant_br_nova",
    "merchant_br_atlas",
)
_GRAPH_ISSUERS = ("bank_br_a", "bank_br_b", "bank_br_c", "itau_br", "nubank_br")


@dataclass(frozen=True)
class LiveDemoTrial:
    trial_id: TrialId
    flow: TrialFlow
    title: str
    description: str
    response_code: str
    secondary_response_code: str
    incident_status: Literal["SUPPORTED", "INCONCLUSIVE"]
    incident_confidence: float
    incident_category: str | None
    alternative_category: str | None
    country: str
    currency: str
    start_offset_minutes: int


_TRIALS: dict[str, LiveDemoTrial] = {
    "deterministic": LiveDemoTrial(
        trial_id="deterministic",
        flow="DETERMINISTIC",
        title="Provider degradation in Mexico",
        description="Five approvals, twelve provider timeouts and eight issuer declines in Mexico are compared with this trial's own healthy baseline.",
        response_code="68",
        secondary_response_code="insufficient_funds",
        incident_status="SUPPORTED",
        incident_confidence=0.82,
        incident_category="PROVIDER_DEGRADATION",
        alternative_category="ISSUER_DECLINE",
        country="MX",
        currency="MXN",
        start_offset_minutes=0,
    ),
    "graph_enriched": LiveDemoTrial(
        trial_id="graph_enriched",
        flow="GRAPH_ENRICHED",
        title="Issuer decline in Brazil",
        description="Five approvals, twelve issuer declines and eight provider timeouts in Brazil create the Incident; precedent retrieval then enriches the investigation.",
        response_code="do_not_honor",
        secondary_response_code="68",
        incident_status="INCONCLUSIVE",
        incident_confidence=0.58,
        incident_category=None,
        alternative_category="ISSUER_OUTAGE",
        country="BR",
        currency="BRL",
        start_offset_minutes=10,
    ),
}


def trial_catalog() -> list[dict[str, str | int]]:
    """Return display-only metadata; neither effects nor ground truth leave this module."""
    return [
        {
            "trial_id": trial.trial_id,
            "flow": trial.flow,
            "title": trial.title,
            "description": trial.description,
            "transaction_count": _TRIAL_COUNT,
        }
        for trial in _TRIALS.values()
    ]


def launch_trial(trial_id: str, *, idempotency_key: str) -> dict[str, object]:
    """Persist an isolated baseline and queue the fixed trial batch.

    The same supplied key gives every internal batch a stable derived key. A
    network retry therefore reuses the original baseline/current batch instead
    of silently adding another reference population.
    """
    trial = _TRIALS.get(trial_id)
    if trial is None:
        raise ValueError("UNKNOWN_LIVE_DEMO_TRIAL")

    start = _BASE_TIME + timedelta(minutes=trial.start_offset_minutes)
    baseline_batch_ids: list[str] = []
    for window_index in range(_BASELINE_WINDOWS):
        response = _submit(
            _transactions_for(trial, phase="baseline", occurred_at=start + timedelta(minutes=window_index)),
            idempotency_key=f"trial:{trial.trial_id}:{idempotency_key}:base:{window_index}",
        )
        baseline_batch_ids.append(str(response["batch_id"]))
        # A trial only queues after a durable, terminal reference exists. This
        # remains the normal worker path and is a no-op on an idempotent retry.
        run_batch_to_completion(
            str(response["batch_id"]), derive_incidents_once_after_batch=True
        )

    current = _submit(
        _transactions_for(trial, phase="trial", occurred_at=start + timedelta(minutes=_BASELINE_WINDOWS)),
        idempotency_key=f"trial:{trial.trial_id}:{idempotency_key}:current",
    )
    return {
        "schema_version": "1.0",
        "trial_id": trial.trial_id,
        "flow": trial.flow,
        "execution_mode": "QUEUED_SAFE",
        "baseline_batch_ids": baseline_batch_ids,
        **current,
    }


def complete_trial_batch(trial_id: str, batch_id: str) -> None:
    """Complete the queued part of a fixed trial and apply its declared RCA state.

    The transaction lifecycle and Incident detector remain the ordinary durable
    path. The bounded presentation profile is applied before the diagnostic
    suggestion is built, so graph context cannot promote its inconclusive cause.
    """
    trial = _TRIALS.get(trial_id)
    if trial is None:
        raise ValueError("UNKNOWN_LIVE_DEMO_TRIAL")
    run_batch_to_completion(
        batch_id,
        derive_incidents_once_after_batch=True,
        incident_transform=lambda incident: _apply_incident_profile(trial, incident),
    )


def _submit(transactions: list[TransactionInput], *, idempotency_key: str) -> dict[str, object]:
    return _create_batch(BatchRequest(schema_version="1.0", idempotency_key=idempotency_key, transactions=transactions))


def _transactions_for(
    trial: LiveDemoTrial, *, phase: Literal["baseline", "trial"], occurred_at: datetime
) -> list[TransactionInput]:
    occurred_at_text = occurred_at.isoformat().replace("+00:00", "Z")
    count = _BASELINE_COUNT if phase == "baseline" else _TRIAL_COUNT
    return [
        _transaction_for(
            trial,
            index=index,
            response_code=_response_code_for(trial, phase=phase, index=index),
            occurred_at=occurred_at_text,
        )
        for index in range(count)
    ]


def _response_code_for(
    trial: LiveDemoTrial, *, phase: Literal["baseline", "trial"], index: int
) -> str:
    if phase == "baseline" or index % (_TRIAL_COUNT // _TRIAL_SUCCESS_COUNT) == 0:
        return "approved"
    if index in _SECONDARY_FAILURE_INDEXES:
        return trial.secondary_response_code
    return trial.response_code


def _apply_incident_profile(trial: LiveDemoTrial, incident: Incident) -> Incident:
    """Constrain a trial's visible RCA result without changing causal identity."""
    confidence_factors = {
        "statistical_strength": 0.82 if trial.incident_status == "SUPPORTED" else 0.74,
        "loss_coverage": 0.84 if trial.incident_status == "SUPPORTED" else 0.61,
        "temporal_consistency": 0.8 if trial.incident_status == "SUPPORTED" else 0.55,
        "data_quality": 0.82 if trial.incident_status == "SUPPORTED" else 0.9,
    }
    alternatives = (
        [RootCauseAlternative(category=trial.alternative_category, confidence=trial.incident_confidence)]
        if trial.alternative_category
        else []
    )
    root_cause = RootCause(
        status=trial.incident_status,
        category=trial.incident_category,
        confidence=trial.incident_confidence,
        confidence_factors=confidence_factors,
        alternatives=alternatives,
    )
    limitations = list(incident.limitations)
    if trial.incident_status == "INCONCLUSIVE":
        limitation = "The fixed graph-enriched trial preserves ambiguity; historical similarity does not confirm a current cause."
        if limitation not in limitations:
            limitations.append(limitation)
    return incident.model_copy(update={
        "state": trial.incident_status,
        "root_cause": root_cause,
        "limitations": limitations,
    })


def _transaction_for(
    trial: LiveDemoTrial, *, index: int, response_code: str, occurred_at: str
) -> TransactionInput:
    if trial.trial_id == "graph_enriched":
        # Vary the dimensions that are not part of the historical precedent.
        # This leaves provider+country+CARD as the strongest eligible slice,
        # which is comparable to the seeded human-confirmed card precedent.
        merchant_id = _GRAPH_MERCHANTS[index % len(_GRAPH_MERCHANTS)]
        issuer_bank = _GRAPH_ISSUERS[index % len(_GRAPH_ISSUERS)]
    else:
        merchant_id = "merchant_mx_01"
        issuer_bank = "bbva_mx"

    return TransactionInput(
        client_reference=f"live-demo-{trial.trial_id}-{response_code}-{index + 1}",
        occurred_at=occurred_at,
        merchant_id=merchant_id,
        provider_id="stripe",
        issuer_bank=issuer_bank,
        country=trial.country,
        currency=trial.currency,
        amount_minor=12990,
        payment_method_category="CARD",
        card_brand="MASTERCARD",
        card_type="CREDIT",
        provider_connection_id="conn_br_stripe_demo",
        channel="WEB",
        provider_response_code=response_code,
    )
