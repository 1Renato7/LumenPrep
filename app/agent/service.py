"""Orchestration of the proactive diagnostic agent.

The agent runs *after* an Incident is persisted, never before and never inside
the decision that creates it:

    persisted Incident
      -> build the immutable EvidencePack
      -> retrieve authorized precedent
      -> ask the injected client for JSON
      -> validate grounding, authority and payment safety
      -> persist the suggestion idempotently, separately from the Incident

Every failure mode below degrades to a typed, honest suggestion.  Nothing here
may raise into the caller: the Incident, the detection and the deterministic
explanation must survive an unavailable or misbehaving model.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any

from app.incidents import Incident
from app.memory import IncidentMemoryService

from .evidence import build_evidence_pack
from .llm import SuggestionClient, TemplateSuggestionClient
from .models import (
    AgentRetrievalTrace,
    DiagnosticSuggestion,
    EvidencePack,
    HUMAN_ONLY_LIMITATION,
)
from .prompt import PROMPT_VERSION
from .repository import DiagnosticSuggestionRepository, suggestion_idempotency_key
from .retrieval import retrieve_precedents
from .validation import FRAUD_DECLINE_CODE, FRAUD_LIMITATION, SuggestionPolicyError, parse_and_validate

logger = logging.getLogger(__name__)

# OPEN-AGT-003's safe fallback: publish a hypothesis only with at least two
# independent current evidences. Below that the honest answer is that we cannot
# support one, not a plausible-sounding guess.
MINIMUM_INDEPENDENT_EVIDENCE = 2


class DiagnosticAgentService:
    """Read-only agent: no payment tool, no Incident write, no cause promotion."""

    def __init__(
        self,
        *,
        client: SuggestionClient | None = None,
        memory_service: IncidentMemoryService | None = None,
        repository: DiagnosticSuggestionRepository | None = None,
        minimum_independent_evidence: int = MINIMUM_INDEPENDENT_EVIDENCE,
    ) -> None:
        self.client = client if client is not None else TemplateSuggestionClient()
        self.memory_service = memory_service
        self.repository = repository if repository is not None else DiagnosticSuggestionRepository()
        self.minimum_independent_evidence = minimum_independent_evidence

    def suggest_for_incident(
        self,
        incident: Incident | Mapping[str, Any],
        *,
        decline_profile: Mapping[str, int] | None = None,
        persist: bool = True,
    ) -> DiagnosticSuggestion:
        pack = build_evidence_pack(incident, decline_profile=decline_profile)
        idempotency_key = suggestion_idempotency_key(
            incident_id=pack.incident_id,
            evidence_fingerprint=pack.evidence_fingerprint,
            model_version=self.client.model_version,
            prompt_version=PROMPT_VERSION,
        )
        if persist:
            existing = self.repository.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                # Same Incident, same facts, same model and prompt: reuse the
                # stored hypothesis instead of paying for a second, divergent one.
                return existing

        trace = retrieve_precedents(pack, memory_service=self.memory_service)
        suggestion = self._generate(pack, trace)
        if persist:
            self.repository.upsert(suggestion, idempotency_key=idempotency_key, prompt_version=PROMPT_VERSION)
        return suggestion

    def _generate(self, pack: EvidencePack, trace: AgentRetrievalTrace) -> DiagnosticSuggestion:
        if pack.independent_evidence_count < self.minimum_independent_evidence:
            return self._insufficient(pack, trace)
        try:
            raw = self.client.suggest(pack, trace)
        except Exception as error:
            logger.warning("diagnostic agent client failed for %s: %s", pack.incident_id, type(error).__name__)
            return self._unavailable(pack, trace, f"the suggestion client failed with {type(error).__name__}")

        try:
            suggestion = parse_and_validate(self._seed(raw, pack, trace), pack=pack, trace=trace)
        except SuggestionPolicyError as error:
            logger.warning("diagnostic agent response rejected for %s: %s", pack.incident_id, error)
            return self._unavailable(pack, trace, f"the model response was rejected by the validator: {error}")
        return self._finalize(suggestion, pack, trace)

    def _seed(self, raw: str, pack: EvidencePack, trace: AgentRetrievalTrace) -> str:
        """Overwrite the identity fields so the model cannot author them.

        ``incident_id``, ``evidence_fingerprint``, ``model_version`` and the
        retrieval trace are facts of this run.  Injecting them before validation
        removes any incentive for the model to guess them, while keeping every
        other field subject to the guardrails.
        """
        try:
            payload = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            return raw if isinstance(raw, str) else ""
        if not isinstance(payload, dict):
            return raw
        payload["incident_id"] = pack.incident_id
        payload["evidence_fingerprint"] = pack.evidence_fingerprint
        payload["model_version"] = self.client.model_version
        payload["retrieval_trace"] = trace.model_dump(mode="json")
        payload["limitations"] = _mandatory_limitations(pack, trace, payload.get("limitations"))
        return json.dumps(payload)

    def _finalize(
        self, suggestion: DiagnosticSuggestion, pack: EvidencePack, trace: AgentRetrievalTrace
    ) -> DiagnosticSuggestion:
        return suggestion.model_copy(
            update={
                "incident_id": pack.incident_id,
                "evidence_fingerprint": pack.evidence_fingerprint,
                "model_version": self.client.model_version,
                "retrieval_trace": trace.model_dump(mode="json"),
            }
        )

    def _insufficient(self, pack: EvidencePack, trace: AgentRetrievalTrace) -> DiagnosticSuggestion:
        limitations = _mandatory_limitations(
            pack,
            trace,
            [
                f"Only {pack.independent_evidence_count} independent current evidence source(s) are available; "
                f"{self.minimum_independent_evidence} are required before publishing a hypothesis."
            ],
        )
        return DiagnosticSuggestion(
            incident_id=pack.incident_id,
            evidence_fingerprint=pack.evidence_fingerprint,
            status="INSUFFICIENT_EVIDENCE",
            suggested_category=None,
            summary_for_operations=(
                "The current evidence does not support a traceable investigation hypothesis for "
                f"{_scope_label(pack)}. The engine's own diagnosis and evidence remain available."
            ),
            executive_summary=(
                "No agent hypothesis is offered for this Incident; the evidence available is not sufficient."
            ),
            reasons=[],
            confidence=0.0,
            recommended_actions=[],
            limitations=limitations,
            retrieval_trace=trace.model_dump(mode="json"),
            model_version=self.client.model_version,
        )

    def _unavailable(self, pack: EvidencePack, trace: AgentRetrievalTrace, reason: str) -> DiagnosticSuggestion:
        return DiagnosticSuggestion(
            incident_id=pack.incident_id,
            evidence_fingerprint=pack.evidence_fingerprint,
            status="UNAVAILABLE",
            suggested_category=None,
            summary_for_operations=(
                "The diagnostic agent is unavailable for this Incident; use the engine's diagnosis, "
                "evidence and deterministic explanation."
            ),
            executive_summary="No agent hypothesis is available for this Incident.",
            reasons=[],
            confidence=0.0,
            recommended_actions=[],
            limitations=_mandatory_limitations(pack, trace, [f"Agent output was withheld because {reason}."]),
            retrieval_trace=trace.model_dump(mode="json"),
            model_version=self.client.model_version,
        )


def _mandatory_limitations(
    pack: EvidencePack, trace: AgentRetrievalTrace, authored: object
) -> list[str]:
    """Limitations the system states itself, derived from facts rather than text."""
    limitations: list[str] = []
    if isinstance(authored, list):
        limitations.extend(str(item) for item in authored if isinstance(item, str) and item.strip())
    limitations.append(HUMAN_ONLY_LIMITATION)
    if trace.status == "NO_PRECEDENT":
        limitations.append(
            "No human-confirmed precedent passed the retrieval threshold; this hypothesis rests on current evidence only."
        )
    elif trace.status == "MEMORY_UNAVAILABLE":
        limitations.append(
            "Incident memory was unavailable, so no precedent could be considered; the engine's causal status is unchanged."
        )
    if FRAUD_DECLINE_CODE in pack.decline_profile:
        limitations.append(FRAUD_LIMITATION)
    if pack.root_cause.status == "INCONCLUSIVE":
        limitations.append(
            "The engine's root cause is INCONCLUSIVE and this suggestion does not change it."
        )
    # Preserve author order while removing duplicates.
    return list(dict.fromkeys(limitations))


def _scope_label(pack: EvidencePack) -> str:
    if not pack.scope:
        return "the observed slice"
    return " x ".join(f"{key}={','.join(values)}" for key, values in sorted(pack.scope.items()))
