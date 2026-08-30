"""CMP-AGT-001 — proactive, read-only diagnostic agent.

The agent runs after an Incident is persisted and proposes a *hypothesis* for a
human to investigate.  It is not the causal authority: ``Incident.root_cause``
stays owned by the deterministic engine, the agent holds no payment tool, and
every action it proposes is ``HUMAN_ONLY``.

Contracts: ``CTR-AGT-001`` EvidencePack, ``CTR-AGT-002`` RetrievalTrace,
``CTR-AGT-003`` DiagnosticSuggestion.
"""

from .evidence import build_evidence_pack
from .llm import OpenAISuggestionClient, SuggestionClient, TemplateSuggestionClient
from .models import (
    AgentRetrievalTrace,
    CausalAlternative,
    DiagnosticSuggestion,
    EngineRootCause,
    EvidenceItem,
    EvidencePack,
    ImpactSummary,
    ObservationWindow,
    RetrievedSource,
    SuggestedAction,
    SuggestionReason,
    evidence_fingerprint_for,
)
from .prompt import PROMPT_VERSION, system_prompt, user_payload
from .repository import DiagnosticSuggestionRepository, suggestion_idempotency_key
from .retrieval import retrieve_precedents
from .service import DiagnosticAgentService
from .validation import SuggestionPolicyError, parse_and_validate

__all__ = [
    "AgentRetrievalTrace",
    "CausalAlternative",
    "DiagnosticAgentService",
    "DiagnosticSuggestion",
    "DiagnosticSuggestionRepository",
    "EngineRootCause",
    "EvidenceItem",
    "EvidencePack",
    "ImpactSummary",
    "ObservationWindow",
    "OpenAISuggestionClient",
    "PROMPT_VERSION",
    "RetrievedSource",
    "SuggestedAction",
    "SuggestionClient",
    "SuggestionPolicyError",
    "SuggestionReason",
    "TemplateSuggestionClient",
    "build_evidence_pack",
    "evidence_fingerprint_for",
    "parse_and_validate",
    "retrieve_precedents",
    "suggestion_idempotency_key",
    "system_prompt",
    "user_payload",
]
