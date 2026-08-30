"""Grounding and payment-safety validation of a model-authored suggestion.

Model text carries no authority.  Before a suggestion may be persisted or shown
it must survive four independent checks:

1. **Shape** — strict JSON against CTR-AGT-003; unknown fields are rejected.
2. **Grounding** — every cited evidence ID exists in the EvidencePack or in an
   authorized retrieved source.  Invented IDs, numbers and precedents fail here.
3. **Authority** — the response may not touch ``root_cause``, may not promote a
   status, and may not assert fraud as established fact.
4. **Payment safety** — every action is ``HUMAN_ONLY`` and investigative.  No
   retry, reroute, refund, capture, cancellation or any payment execution.

A failure raises ``SuggestionPolicyError``.  The caller turns that into an
``UNAVAILABLE`` suggestion; it never silently downgrades to a valid hypothesis.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from .models import AgentRetrievalTrace, DiagnosticSuggestion, EvidencePack

# Keys the deterministic engine owns.  Their presence in a model response is an
# attempted authority grab, not a formatting mistake.
ENGINE_OWNED_KEYS = frozenset(
    {
        "root_cause",
        "root_cause_status",
        "root_cause_category",
        "state",
        "incident_state",
        "impact",
        "metrics",
        "scope",
        "evidence",
        "memory_matches",
        "execution_override",
    }
)

# Verbs that move money or traffic.  This challenge diagnoses; it never remediates.
FINANCIAL_ACTION_PATTERN = re.compile(
    r"\b("
    r"retry|retries|retrying|reroute|re-route|rerouting|refund|refunds|refunding|"
    r"capture|captures|capturing|chargeback|void|voiding|settle|settling|"
    r"cancel|cancels|cancelling|canceling|cancellation|"
    r"authorize|authorise|authorization|authorisation|"
    r"charge|charges|charging|failover|fail-over|"
    r"switch traffic|shift traffic|disable the provider|execute the payment|process the payment"
    r")\b",
    re.IGNORECASE,
)

# Fraud is an accusation. A decline code is not a verdict, so confirmatory
# phrasing is rejected even when SUSPECTED_FRAUD dominates the decline profile.
FRAUD_ASSERTION_PATTERN = re.compile(
    r"\b("
    r"confirmed fraud|fraud confirmed|proven fraud|fraud is confirmed|fraud is proven|"
    r"is fraud|was fraud|fraudulent transactions were|established fraud|"
    r"fraude confirmada|fraude comprovada"
    r")\b",
    re.IGNORECASE,
)

FORBIDDEN_CATEGORIES = frozenset({"FRAUD", "CONFIRMED_FRAUD", "FRAUD_CONFIRMED", "PROVEN_FRAUD"})

# The engine's own vocabulary for a settled cause. A hypothesis may not borrow it.
PROMOTION_PATTERN = re.compile(r"\b(SUPPORTED|HUMAN_CONFIRMED|root cause is confirmed|confirmed root cause)\b")

FRAUD_DECLINE_CODE = "SUSPECTED_FRAUD"
FRAUD_LIMITATION = (
    "A SUSPECTED_FRAUD decline code is a risk-control signal reported by the issuer or provider, "
    "not proof of fraud; treat this as a possible block by risk controls until a human confirms it."
)


class SuggestionPolicyError(ValueError):
    """The model response violated shape, grounding, authority or payment policy."""


def parse_and_validate(
    raw_response: str,
    *,
    pack: EvidencePack,
    trace: AgentRetrievalTrace,
) -> DiagnosticSuggestion:
    """Parse strict JSON from the model and enforce every guardrail."""
    payload = _parse_json_object(raw_response)
    _reject_engine_authority(payload)
    suggestion = _parse_contract(payload)
    _validate_grounding(suggestion, pack=pack, trace=trace)
    _validate_actions(suggestion)
    _validate_language(suggestion, pack=pack)
    _validate_status_rules(suggestion)
    return suggestion


def _parse_json_object(raw_response: str) -> dict[str, Any]:
    if not isinstance(raw_response, str) or not raw_response.strip():
        raise SuggestionPolicyError("model returned an empty response")
    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError as error:
        raise SuggestionPolicyError(f"model response is not valid JSON: {error.msg}") from error
    if not isinstance(payload, dict):
        raise SuggestionPolicyError("model response must be a JSON object")
    return payload


def _reject_engine_authority(payload: dict[str, Any]) -> None:
    """Fail loudly when the model tries to write an engine-owned field.

    ``extra="forbid"`` would also reject these, but a named error keeps the
    audit trail honest about *what* was attempted.
    """
    intruders = sorted(ENGINE_OWNED_KEYS & set(payload))
    if intruders:
        raise SuggestionPolicyError(
            f"model attempted to write engine-owned fields: {intruders}; "
            "root cause and Incident state belong to the deterministic engine"
        )
    status = payload.get("status")
    if isinstance(status, str) and status.upper() in {"SUPPORTED", "INCONCLUSIVE", "HUMAN_CONFIRMED"}:
        raise SuggestionPolicyError(
            f"model attempted to return the engine's causal status {status!r}; "
            "a suggestion may only be SUGGESTED, INSUFFICIENT_EVIDENCE or UNAVAILABLE"
        )


def _parse_contract(payload: dict[str, Any]) -> DiagnosticSuggestion:
    try:
        return DiagnosticSuggestion.model_validate(payload)
    except ValidationError as error:
        raise SuggestionPolicyError(f"model response does not match CTR-AGT-003: {error.error_count()} error(s)") from error


def _validate_grounding(
    suggestion: DiagnosticSuggestion,
    *,
    pack: EvidencePack,
    trace: AgentRetrievalTrace,
) -> None:
    allowed = set(pack.authorized_evidence_ids) | set(trace.authorized_evidence_ids)
    cited: set[str] = set()
    for reason in suggestion.reasons:
        cited.update(reason.evidence_ids)
    for action in suggestion.recommended_actions:
        cited.update(action.rationale_evidence_ids)
    invented = sorted(cited - allowed)
    if invented:
        raise SuggestionPolicyError(
            f"suggestion cites evidence IDs that do not exist in the EvidencePack or an authorized source: {invented}"
        )


def _validate_actions(suggestion: DiagnosticSuggestion) -> None:
    for action in suggestion.recommended_actions:
        if action.execution != "HUMAN_ONLY":
            raise SuggestionPolicyError(f"recommended action execution must be HUMAN_ONLY, got {action.execution!r}")
        match = FINANCIAL_ACTION_PATTERN.search(action.action)
        if match:
            raise SuggestionPolicyError(
                f"recommended action proposes the financial or traffic operation {match.group(0)!r}; "
                "the agent may only propose investigation steps"
            )


def _validate_language(suggestion: DiagnosticSuggestion, *, pack: EvidencePack) -> None:
    narrative = " ".join(
        [suggestion.summary_for_operations, suggestion.executive_summary]
        + [reason.statement for reason in suggestion.reasons]
        + [suggestion.suggested_category or ""]
    )
    fraud = FRAUD_ASSERTION_PATTERN.search(narrative)
    if fraud:
        raise SuggestionPolicyError(
            f"suggestion asserts fraud as established fact ({fraud.group(0)!r}); "
            "a decline code alone does not prove fraud"
        )
    if (suggestion.suggested_category or "").upper() in FORBIDDEN_CATEGORIES:
        raise SuggestionPolicyError(
            f"suggested_category {suggestion.suggested_category!r} states fraud as a confirmed category"
        )
    promotion = PROMOTION_PATTERN.search(narrative)
    if promotion:
        raise SuggestionPolicyError(
            f"suggestion uses the engine's confirmation vocabulary {promotion.group(0)!r}; "
            "a hypothesis may not promote the current cause"
        )
    if FRAUD_DECLINE_CODE in pack.decline_profile and suggestion.status == "SUGGESTED":
        if not any(FRAUD_DECLINE_CODE in limitation for limitation in suggestion.limitations):
            raise SuggestionPolicyError(
                "the observed window contains SUSPECTED_FRAUD declines, so the suggestion must state that "
                "limitation explicitly"
            )


def _validate_status_rules(suggestion: DiagnosticSuggestion) -> None:
    if suggestion.status != "SUGGESTED":
        if suggestion.suggested_category is not None:
            raise SuggestionPolicyError(f"{suggestion.status} must not name a suggested_category")
        if suggestion.confidence != 0.0:
            raise SuggestionPolicyError(f"{suggestion.status} must report zero confidence")
        return
    grounded_reasons = [reason for reason in suggestion.reasons if reason.evidence_ids]
    if not grounded_reasons:
        raise SuggestionPolicyError("SUGGESTED requires at least one reason backed by an evidence ID")
    if not suggestion.recommended_actions:
        raise SuggestionPolicyError("SUGGESTED requires at least one HUMAN_ONLY investigation step")
