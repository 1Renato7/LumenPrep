"""CTR-AGT-002 retrieval over the memory the system already has.

Per ``OPEN-AGT-002``'s safe fallback this layer reads only two authorized,
versioned sources: the structured Incident memory (Neo4j primary, deterministic
local fallback) and the playbook catalog.  No vector store, no embeddings, no
web retrieval, no new corpus.

Retrieved text is *data*.  It can widen the set of evidence IDs the agent is
allowed to cite; it can never widen the agent's authority.  ``NO_PRECEDENT`` is
therefore a fact recorded in the trace, not a reason to stop investigating.
"""

from __future__ import annotations

from datetime import datetime

from app.config import settings
from app.explanation.catalog import CATALOG_SCHEMA_VERSION, load_playbooks
from app.explanation.grounded import Playbook
from app.memory import (
    IncidentMemoryService,
    InMemoryIncidentRepository,
    Neo4jIncidentRepository,
)
from app.memory.models import Incident as MemoryIncident
from app.memory.models import MemoryStatus
from app.memory.repository import IncidentMemoryRepository
from app.memory.seed import seed_mastercard_d2

from .models import AgentRetrievalTrace, EvidencePack, RetrievedSource

MEMORY_FILTER = "confirmation = 'HUMAN_CONFIRMED' AND shared_scope = true"


def retrieve_precedents(
    pack: EvidencePack,
    *,
    memory_service: IncidentMemoryService | None = None,
    playbooks: tuple[Playbook, ...] | None = None,
) -> AgentRetrievalTrace:
    """Return an authorized, traceable view of precedent for this Incident.

    A retrieval failure degrades to ``MEMORY_UNAVAILABLE`` with an empty source
    list rather than raising: losing memory must not lose the suggestion.
    """
    service = memory_service if memory_service is not None else _default_memory_service(pack)
    catalog = playbooks if playbooks is not None else _load_catalog()

    sources: list[RetrievedSource] = []
    authorized: set[str] = set(pack.authorized_evidence_ids)

    try:
        result = service.retrieve(_memory_query(pack))
    except Exception:
        status = MemoryStatus.MEMORY_UNAVAILABLE
        candidate_count = 0
        index_version = "structured-v1"
        fallback_used = False
    else:
        status = result.memory_status
        candidate_count = result.retrieval_trace.candidate_count
        index_version = result.retrieval_trace.index_version
        fallback_used = result.retrieval_trace.fallback_used
        for match in result.matches:
            authorized.update(match.evidence_ids)
            sources.append(
                RetrievedSource(
                    source="incident_memory",
                    source_id=match.incident_id,
                    version=index_version,
                    score=match.structured_score,
                    summary=(
                        f"Human-confirmed precedent {match.incident_id} "
                        f"({match.occurred_at.isoformat()}) with confirmed cause "
                        f"{match.confirmed_cause}; matching factors: "
                        f"{', '.join(match.matching_factors) or 'none recorded'}."
                    ),
                    evidence_ids=list(match.evidence_ids),
                )
            )

    for playbook in _applicable_playbooks(pack, catalog):
        sources.append(
            RetrievedSource(
                source="playbook_catalog",
                source_id=playbook.playbook_id,
                version=CATALOG_SCHEMA_VERSION,
                score=None,
                summary=playbook.action,
                evidence_ids=[],
            )
        )

    return AgentRetrievalTrace(
        incident_id=pack.incident_id,
        status=status.value,
        filter_criteria=MEMORY_FILTER,
        candidate_count=candidate_count,
        index_version=index_version,
        fallback_used=fallback_used,
        sources=sources,
        authorized_evidence_ids=sorted(authorized),
    )


def _applicable_playbooks(pack: EvidencePack, catalog: tuple[Playbook, ...]) -> list[Playbook]:
    """Offer investigation templates for the engine's cause and its alternatives.

    A playbook is a versioned suggestion of what a human might check.  It never
    authorizes execution: the catalog loader already rejects any entry whose
    ``execution`` is not ``HUMAN_ONLY``.
    """
    categories = {pack.root_cause.category} | {item.category for item in pack.rca_alternatives}
    categories.discard(None)
    selected = [
        playbook
        for playbook in catalog
        if playbook.cause_categories & categories
        and all(required <= set(pack.scope.get(key, ())) for key, required in playbook.required_scope.items())
    ]
    generic = [playbook for playbook in catalog if playbook.playbook_id == "PB-GENERIC-INVESTIGATION"]
    return selected or generic


def _memory_query(pack: EvidencePack) -> MemoryIncident:
    """Adapt CTR-AGT-001 to the CTR-MEM-001 query shape without re-deriving facts."""
    return MemoryIncident(
        incident_id=pack.incident_id,
        detected_at=_parse_timestamp(pack.window.end),
        scope={key: tuple(values) for key, values in pack.scope.items()},
        metrics={"decline_codes": sorted(pack.decline_profile)},
        root_cause_status=pack.root_cause.status,
        root_cause_category=pack.root_cause.category,
        evidence_ids=tuple(pack.authorized_evidence_ids),
        correlation_id=pack.correlation_id,
    )


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _load_catalog() -> tuple[Playbook, ...]:
    try:
        return load_playbooks()
    except (OSError, ValueError):
        # A broken catalog is an operational problem, not a reason to abort the
        # suggestion; the trace simply carries no playbook source.
        return ()


def _default_memory_service(pack: EvidencePack) -> IncidentMemoryService:
    """Mirror the API's wiring: Neo4j when configured, local fallback otherwise."""
    fallback = InMemoryIncidentRepository()
    seed_mastercard_d2(fallback, now=_parse_timestamp(pack.window.end))
    primary = _neo4j_repository()
    if primary is None:
        return IncidentMemoryService(fallback)
    return IncidentMemoryService(primary, fallback=fallback)


_neo4j_driver: object | None = None
_neo4j_driver_failed = False


def _neo4j_repository() -> IncidentMemoryRepository | None:
    """Build the driver once per process, mirroring the incidents API.

    The agent runs on every persisted Incident, so constructing a driver per
    call would open a connection pool per Incident and never close any of them.
    A construction failure disables the driver for the process; the local
    fallback repository keeps retrieval working.
    """
    global _neo4j_driver, _neo4j_driver_failed
    if not settings.neo4j_uri or _neo4j_driver_failed:
        return None
    if _neo4j_driver is None:
        try:
            from neo4j import GraphDatabase

            _neo4j_driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
        except Exception:
            _neo4j_driver_failed = True
            return None
    return Neo4jIncidentRepository(
        _neo4j_driver,
        database=settings.neo4j_database,
        include_evaluation=False,
    )
