"""CTR-AGT-001..003 v1 — the agent's read-only input and its suggestion output.

Three separate contracts keep the causal authority where the plan puts it:

* ``EvidencePack`` (CTR-AGT-001) is an immutable projection of facts the
  deterministic engine already computed and persisted.  The agent receives this
  object and nothing else — no connection, no SQL, no credential, no tool.
* ``AgentRetrievalTrace`` (CTR-AGT-002) records what structured memory returned,
  including ``NO_PRECEDENT``.  Absence of a precedent is data, never an
  instruction to stop investigating.
* ``DiagnosticSuggestion`` (CTR-AGT-003) is a labelled hypothesis.  It is not
  ``Incident.root_cause``, it never promotes a cause, and every action it
  proposes is ``HUMAN_ONLY``.
"""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

AGENT_SCHEMA_VERSION: Literal["1.0"] = "1.0"


class EvidenceItem(BaseModel):
    """One already-persisted evidence row the agent is allowed to cite."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)


class CausalAlternative(BaseModel):
    """A competing hypothesis the RCA already ranked; not a cause."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    category: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)


class EngineRootCause(BaseModel):
    """Read-only mirror of the engine-owned diagnosis.

    The agent is given the current causal state so it can avoid contradicting
    it.  Nothing in the agent path may write back to this value.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["SUPPORTED", "INCONCLUSIVE"]
    category: str | None
    confidence: float = Field(ge=0, le=1)


class ObservationWindow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    start: str = Field(min_length=1)
    end: str = Field(min_length=1)


class ImpactSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metric: str = Field(min_length=1)
    method: str = Field(min_length=1)
    amount_minor: int = Field(ge=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")


class RefusalCodeSummary(BaseModel):
    """CTR-RFC-002: a persisted, scope-limited reason aggregate."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    provider_id: str = Field(min_length=1)
    issuer_bank: str = Field(min_length=1)
    card_brand: str = Field(min_length=1)
    response_code: str = Field(min_length=1)
    normalized_code: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    source: str = Field(min_length=1)
    mapping_version: str = Field(min_length=1)
    transaction_count: int = Field(ge=1)
    evidence_id: str = Field(min_length=1)


class EvidencePack(BaseModel):
    """CTR-AGT-001 v1 — immutable fact bundle handed to the agent."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = AGENT_SCHEMA_VERSION
    incident_id: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    evidence_fingerprint: str = ""
    scope: dict[str, list[str]]
    window: ObservationWindow
    approval_rate_observed: float | None = None
    approval_rate_expected: float | None = None
    eligible_attempts: int = Field(default=0, ge=0)
    lost_approvals: int = Field(default=0, ge=0)
    impact: ImpactSummary
    detector_evidence: list[EvidenceItem] = Field(default_factory=list)
    rca_alternatives: list[CausalAlternative] = Field(default_factory=list)
    decline_profile: dict[str, int] = Field(default_factory=dict)
    refusal_code_summaries: list[RefusalCodeSummary] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    authorized_evidence_ids: list[str] = Field(default_factory=list)
    root_cause: EngineRootCause
    engine_version: str = Field(min_length=1)

    @property
    def independent_evidence_count(self) -> int:
        """Count distinct evidence sources, not repeated citations of one source.

        Two rows produced from the same ``source_ref`` describe one observation
        seen twice.  ``OPEN-AGT-003``'s safe fallback asks for two *independent*
        current evidences before any hypothesis may be published.
        """
        return len({item.source_ref for item in self.detector_evidence})


def evidence_fingerprint_for(pack: EvidencePack) -> str:
    """Fingerprint the facts, excluding the fingerprint field itself.

    Re-running the agent over an unchanged Incident must land on the same
    idempotency key, so the digest has to be stable across processes.
    """
    payload = pack.model_dump(mode="json")
    payload.pop("evidence_fingerprint", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()[:32]


def sealed(pack: EvidencePack) -> EvidencePack:
    """Return the pack carrying its own content fingerprint."""
    return pack.model_copy(update={"evidence_fingerprint": evidence_fingerprint_for(pack)})


class RetrievedSource(BaseModel):
    """One authorized source the retrieval layer returned, with its provenance."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    score: float | None = None
    summary: str = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)


class AgentRetrievalTrace(BaseModel):
    """CTR-AGT-002 v1 — what was retrieved, from where, and under which filter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = AGENT_SCHEMA_VERSION
    incident_id: str = Field(min_length=1)
    status: Literal["MATCH_FOUND", "NO_PRECEDENT", "MEMORY_UNAVAILABLE"]
    filter_criteria: str = Field(min_length=1)
    candidate_count: int = Field(ge=0)
    index_version: str = Field(min_length=1)
    fallback_used: bool = False
    sources: list[RetrievedSource] = Field(default_factory=list)
    authorized_evidence_ids: list[str] = Field(default_factory=list)


class SuggestionReason(BaseModel):
    model_config = ConfigDict(extra="forbid")

    statement: str = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)


class SuggestedAction(BaseModel):
    """An investigative next step. ``execution`` is a constant, not a choice."""

    model_config = ConfigDict(extra="forbid")

    action: str = Field(min_length=1)
    execution: Literal["HUMAN_ONLY"] = "HUMAN_ONLY"
    rationale_evidence_ids: list[str] = Field(default_factory=list)


class DiagnosticSuggestion(BaseModel):
    """CTR-AGT-003 v1 — a hypothesis for a human, never a confirmed cause."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = AGENT_SCHEMA_VERSION
    incident_id: str = Field(min_length=1)
    evidence_fingerprint: str = Field(min_length=1)
    status: Literal["SUGGESTED", "INSUFFICIENT_EVIDENCE", "UNAVAILABLE"]
    suggested_category: str | None = None
    summary_for_operations: str = Field(min_length=1)
    executive_summary: str = Field(min_length=1)
    reasons: list[SuggestionReason] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)
    recommended_actions: list[SuggestedAction] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    retrieval_trace: dict[str, Any] = Field(default_factory=dict)
    model_version: str = Field(min_length=1)


HUMAN_ONLY_LIMITATION = (
    "This is an agent hypothesis for investigation, not the engine's confirmed cause; "
    "every recommended action is HUMAN_ONLY and the system executes no payment action."
)
