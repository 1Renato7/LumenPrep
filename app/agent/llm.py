"""Injectable suggestion clients.

Two implementations share one interface so the orchestration, the guardrails and
the tests are identical regardless of who writes the JSON:

* ``TemplateSuggestionClient`` is the default.  It is deterministic, offline and
  composes its answer strictly from the EvidencePack and the RetrievalTrace, so
  the demo never depends on an API key and the worker never waits on a network
  call inside its DuckDB transaction.
* ``OpenAISuggestionClient`` is opt-in.  It is constructed only when a caller
  explicitly asks for it and a key is configured.

Both return raw text.  Neither is trusted: ``validation.parse_and_validate``
runs over the output either way.
"""

from __future__ import annotations

import json
from typing import Protocol

from .models import AgentRetrievalTrace, DiagnosticSuggestion, EvidencePack, SuggestedAction, SuggestionReason
from .prompt import system_prompt, user_payload

TEMPLATE_MODEL_VERSION = "deterministic-template-v1"


class SuggestionClient(Protocol):
    """Anything that can turn a pack plus a trace into candidate JSON."""

    model_version: str

    def suggest(self, pack: EvidencePack, trace: AgentRetrievalTrace) -> str: ...


class TemplateSuggestionClient:
    """Compose a grounded hypothesis without calling a model.

    This is not a stub: it is the safe production default.  Every sentence is
    built from a persisted number or a persisted evidence row, which is exactly
    the constraint the LLM path is validated against.
    """

    model_version = TEMPLATE_MODEL_VERSION

    def suggest(self, pack: EvidencePack, trace: AgentRetrievalTrace) -> str:
        category = _hypothesis_category(pack)
        reasons = _reasons(pack, trace)
        actions = _actions(pack, trace)
        suggestion = DiagnosticSuggestion(
            incident_id=pack.incident_id,
            evidence_fingerprint=pack.evidence_fingerprint,
            status="SUGGESTED",
            suggested_category=category,
            summary_for_operations=_operations_summary(pack, category),
            executive_summary=_executive_summary(pack),
            reasons=reasons,
            confidence=round(min(pack.root_cause.confidence, 0.75), 4),
            recommended_actions=actions,
            limitations=[],
            retrieval_trace=trace.model_dump(mode="json"),
            model_version=self.model_version,
        )
        return suggestion.model_dump_json()


def _hypothesis_category(pack: EvidencePack) -> str:
    """Reuse a category the engine already produced; never coin a new one."""
    if pack.root_cause.category:
        return pack.root_cause.category
    if pack.rca_alternatives:
        return pack.rca_alternatives[0].category
    return "UNCLASSIFIED_DEGRADATION"


def _scope_label(pack: EvidencePack) -> str:
    if not pack.scope:
        return "the observed slice"
    return " x ".join(f"{key}={','.join(values)}" for key, values in sorted(pack.scope.items()))


def _rate_clause(pack: EvidencePack) -> str:
    if pack.approval_rate_observed is None or pack.approval_rate_expected is None:
        return f"{pack.lost_approvals} approvals were lost across {pack.eligible_attempts} eligible attempts"
    return (
        f"approval rate is {pack.approval_rate_observed:.2%} against an expected "
        f"{pack.approval_rate_expected:.2%} across {pack.eligible_attempts} eligible attempts"
    )


def _operations_summary(pack: EvidencePack, category: str) -> str:
    return (
        f"Investigation hypothesis for {_scope_label(pack)}: {category.replace('_', ' ').lower()} "
        f"between {pack.window.start} and {pack.window.end}, where {_rate_clause(pack)}. "
        "This is a hypothesis to investigate, not the engine's confirmed cause."
    )


def _executive_summary(pack: EvidencePack) -> str:
    return (
        f"About {pack.impact.amount_minor / 100:,.2f} {pack.impact.currency} of GMV is at risk on "
        f"{_scope_label(pack)}; a human review is required."
    )


def _reasons(pack: EvidencePack, trace: AgentRetrievalTrace) -> list[SuggestionReason]:
    reasons: list[SuggestionReason] = []
    decline_evidence = [item for item in pack.detector_evidence if item.kind == "DECLINE_PROFILE"]
    # One detector candidate can carry several evidence refs. Grouping by
    # statement keeps every ID citable without repeating the same sentence.
    grouped: dict[str, list[str]] = {}
    for item in pack.detector_evidence:
        if item.kind == "DECLINE_PROFILE":
            continue
        grouped.setdefault(item.statement, []).append(item.evidence_id)
    for statement, evidence_ids in list(grouped.items())[:3]:
        reasons.append(SuggestionReason(statement=statement, evidence_ids=evidence_ids))
    dominant_decline = _dominant_decline(pack)
    if dominant_decline is not None and decline_evidence:
        code, count = dominant_decline
        reasons.append(
            SuggestionReason(
                statement=(
                    f"The failure signature is dominated by {code} on {count} declined attempts, "
                    "which narrows where to look first."
                ),
                evidence_ids=[item.evidence_id for item in decline_evidence],
            )
        )
    for source in trace.sources:
        if source.source == "incident_memory" and source.evidence_ids:
            reasons.append(
                SuggestionReason(
                    statement=(
                        f"A human-confirmed precedent ({source.source_id}) shares part of this scope; "
                        "it is prior context, not the current cause."
                    ),
                    evidence_ids=list(source.evidence_ids),
                )
            )
    return reasons


def _dominant_decline(pack: EvidencePack) -> tuple[str, int] | None:
    """Pick the leading *decline*, ignoring the outcome sentinels.

    ``NO_DECLINE`` counts approvals and ``NOT_APPLICABLE`` counts methods with
    no issuer decline, so either one winning the raw count would describe the
    healthy part of the window as the failure signature.
    """
    declines = {
        code: count
        for code, count in pack.decline_profile.items()
        if code not in {"NO_DECLINE", "NOT_APPLICABLE"} and count > 0
    }
    if not declines:
        return None
    return max(declines.items(), key=lambda entry: (entry[1], entry[0]))


def _actions(pack: EvidencePack, trace: AgentRetrievalTrace) -> list[SuggestedAction]:
    """Propose investigation steps only; the playbook supplies wording, not authority."""
    rationale = [item.evidence_id for item in pack.detector_evidence[:2]]
    actions = [
        SuggestedAction(
            action=(
                f"Verify the current operational status reported for {_scope_label(pack)} "
                "and compare it against the baseline window."
            ),
            rationale_evidence_ids=rationale,
        ),
        SuggestedAction(
            action="Escalate to the payment operations owner for this scope with the evidence above.",
            rationale_evidence_ids=rationale,
        ),
    ]
    playbooks = [source for source in trace.sources if source.source == "playbook_catalog"]
    if playbooks:
        actions.insert(
            0,
            SuggestedAction(action=playbooks[0].summary, rationale_evidence_ids=rationale),
        )
    return actions


class OpenAISuggestionClient:
    """Opt-in OpenAI client. Never constructed implicitly and never used in tests.

    ``openai`` is deliberately not a declared dependency: the Docker image
    installs a frozen lock without it, so this path is only reachable where an
    operator installed the SDK on purpose.
    """

    def __init__(self, *, api_key: str, model: str = "gpt-4o-mini", timeout: float = 20.0) -> None:
        if not api_key:
            raise ValueError("OpenAISuggestionClient requires an API key")
        try:
            from openai import OpenAI
        except ImportError as error:  # pragma: no cover - depends on optional install
            raise RuntimeError(
                "The OpenAI SDK is not installed; the agent stays on the deterministic client."
            ) from error
        self._client = OpenAI(api_key=api_key, timeout=timeout)
        self._model = model
        self.model_version = f"openai:{model}"

    def suggest(self, pack: EvidencePack, trace: AgentRetrievalTrace) -> str:  # pragma: no cover - network path
        response = self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt()},
                {"role": "user", "content": user_payload(pack, trace)},
            ],
        )
        content = response.choices[0].message.content
        # An empty completion is a technical failure, not a hypothesis. Returning
        # "{}" keeps the single rejection path in the validator.
        return content if isinstance(content, str) and content.strip() else json.dumps({})
