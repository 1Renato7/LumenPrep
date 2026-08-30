"""Grounded links from transaction records to an already-derived Incident."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from app.explanation.grounded import ExplanationBundle
from app.memory.models import Incident


@dataclass(frozen=True)
class TransactionEvidenceTrace:
    """Authorized transaction evidence for one Incident, in stable order."""

    incident_id: str
    transaction_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class TransactionIncidentLink:
    """One scope-validated Incident link for a transaction.

    ``evidence_ids`` are the evidence IDs authorized by the transaction
    classification.  Incident evidence is kept separate because the
    ExplanationBundle may also contain historical evidence IDs; mixing those
    namespaces would make a precedent look like current transaction evidence.
    """

    incident_id: str
    evidence_ids: tuple[str, ...]
    incident_evidence_ids: tuple[str, ...]
    explanation: ExplanationBundle | None
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class TransactionGrounding:
    """Grounded transaction detail assembled without a per-transaction LLM call."""

    transaction_id: str
    incident_links: tuple[TransactionIncidentLink, ...]
    rejected_incident_ids: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @property
    def incident_ids(self) -> tuple[str, ...]:
        return tuple(link.incident_id for link in self.incident_links)

    @property
    def evidence_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted({evidence_id for link in self.incident_links for evidence_id in link.evidence_ids})
        )

    @property
    def status(self) -> str:
        if not self.incident_links:
            return "NO_INCIDENT"
        if self.rejected_incident_ids or any(link.explanation is None for link in self.incident_links):
            return "PARTIAL"
        return "RESOLVED"

    @property
    def short_summary(self) -> str:
        """Return a deterministic short summary from existing bundles only."""

        if not self.incident_links:
            return "No related Incident was resolved for this transaction."
        summaries = [
            link.explanation.executive_summary
            for link in self.incident_links
            if link.explanation is not None
        ]
        if summaries:
            return " ".join(dict.fromkeys(summaries))
        return "Related incident resolved; ExplanationBundle is unavailable."

    def to_contract(self) -> dict[str, object]:
        """Serialize the detail without inventing an explanation or evidence."""

        return {
            "transaction_id": self.transaction_id,
            "status": self.status,
            "incident_ids": list(self.incident_ids),
            "evidence_ids": list(self.evidence_ids),
            "incidents": [
                {
                    "incident_id": link.incident_id,
                    "evidence_ids": list(link.evidence_ids),
                    "incident_evidence_ids": list(link.incident_evidence_ids),
                    "explanation": link.explanation.to_contract() if link.explanation is not None else None,
                    "limitations": list(link.limitations),
                }
                for link in self.incident_links
            ],
            "rejected_incident_ids": list(self.rejected_incident_ids),
            "limitations": list(self.limitations),
            "short_summary": self.short_summary,
        }


def resolve_transaction_evidence(
    incident: Incident,
    transaction_records: Iterable[Mapping[str, object]],
) -> TransactionEvidenceTrace:
    """Resolve only evidence jointly authorized by the record and the Incident.

    A transaction becomes traceable to an Incident only when its classification
    names that Incident, shares the Incident correlation ID, and contains at
    least one classification evidence ID. Transaction evidence and aggregated
    Incident evidence intentionally have separate namespaces. Historical-memory
    evidence is excluded because it describes a precedent, not a raw current
    transaction.
    """
    resolved: dict[str, set[str]] = {}

    for record in transaction_records:
        transaction_id = record.get("transaction_id")
        classification = record.get("classification")
        if not isinstance(transaction_id, str) or not isinstance(classification, Mapping):
            continue
        if record.get("correlation_id") != incident.correlation_id:
            continue
        related_incident_ids = _as_strings(classification.get("related_incident_ids"))
        if incident.incident_id not in related_incident_ids:
            continue
        classification_evidence = set(_as_strings(classification.get("evidence_ids")))
        if classification_evidence:
            resolved.setdefault(transaction_id, set()).update(classification_evidence)

    transaction_ids = tuple(sorted(resolved))
    evidence_ids = tuple(sorted({evidence_id for values in resolved.values() for evidence_id in values}))
    return TransactionEvidenceTrace(
        incident_id=incident.incident_id,
        transaction_ids=transaction_ids,
        evidence_ids=evidence_ids,
    )


def resolve_transaction_grounding(
    transaction_id: str,
    transaction_records: Iterable[Mapping[str, object]],
    incidents: Mapping[str, Incident] | Iterable[Incident],
    explanations: Mapping[str, ExplanationBundle] | None = None,
    explanation_failures: Mapping[str, str] | None = None,
) -> TransactionGrounding:
    """Resolve ``transaction_id -> evidence -> Incident -> ExplanationBundle``.

    Only records for ``transaction_id`` are considered.  A link is authorized
    when its classification names an existing Incident, carries at least one
    classification evidence ID, and has the Incident's correlation ID.  The
    resolver never generates a bundle: callers pass the already-computed
    Incident bundles, so model and memory failures remain visible in their
    existing ``limitations`` and ``model_version`` fields.
    """

    incident_by_id = _incident_map(incidents)
    bundles = explanations or {}
    failures = explanation_failures or {}
    evidence_by_incident: dict[str, set[str]] = {}
    rejected: set[str] = set()

    for record in transaction_records:
        if record.get("transaction_id") != transaction_id:
            continue
        classification = record.get("classification")
        if not isinstance(classification, Mapping):
            continue
        related_ids = _as_strings(classification.get("related_incident_ids"))
        classification_evidence = set(_as_strings(classification.get("evidence_ids")))
        if not classification_evidence:
            rejected.update(related_ids)
            continue
        correlation_id = record.get("correlation_id")
        for incident_id in related_ids:
            incident = incident_by_id.get(incident_id)
            if incident is None or correlation_id != incident.correlation_id:
                rejected.add(incident_id)
                continue
            evidence_by_incident.setdefault(incident_id, set()).update(classification_evidence)

    links: list[TransactionIncidentLink] = []
    limitations: list[str] = []
    for incident_id in sorted(evidence_by_incident):
        incident = incident_by_id[incident_id]
        bundle = bundles.get(incident_id)
        link_limitations: list[str] = []
        if bundle is None:
            failure = failures.get(incident_id)
            if failure:
                link_limitations.append(failure)
            else:
                link_limitations.append(
                    "ExplanationBundle is unavailable; no new model call was made for this transaction."
                )
        else:
            if bundle.incident_id != incident_id:
                link_limitations.append("ExplanationBundle incident_id did not match the resolved Incident.")
            link_limitations.extend(bundle.limitations)
        links.append(
            TransactionIncidentLink(
                incident_id=incident_id,
                evidence_ids=tuple(sorted(evidence_by_incident[incident_id])),
                incident_evidence_ids=tuple(incident.evidence_ids),
                explanation=bundle if bundle is not None and bundle.incident_id == incident_id else None,
                limitations=tuple(dict.fromkeys(link_limitations)),
            )
        )
        limitations.extend(f"{incident_id}: {item}" for item in link_limitations)

    if not links:
        limitations.append("No related Incident with authorized evidence was resolved for this transaction.")
    if rejected:
        limitations.append("Some related incident IDs were rejected by existence, scope, or evidence validation.")
    return TransactionGrounding(
        transaction_id=transaction_id,
        incident_links=tuple(links),
        rejected_incident_ids=tuple(sorted(rejected)),
        limitations=tuple(dict.fromkeys(limitations)),
    )


def resolve_transaction_grounding_from_api_responses(
    transaction_id: str,
    transaction_records: Iterable[Mapping[str, object]],
    incident_responses: Mapping[str, Mapping[str, object]],
) -> TransactionGrounding:
    """Adapt existing ``GET /incidents/{id}`` response bodies for transaction detail.

    This is deliberately not an HTTP client and does not introduce a transaction
    endpoint or public schema. The future API handler supplies the transaction
    records and already-read incident responses. Invalid or unavailable bundles
    become explicit ``PARTIAL`` limitations rather than triggering an LLM call.
    """

    incidents: dict[str, Incident] = {}
    bundles: dict[str, ExplanationBundle] = {}
    failures: dict[str, str] = {}
    for response in incident_responses.values():
        incident_payload = response.get("incident")
        if not isinstance(incident_payload, Mapping):
            continue
        try:
            incident = Incident.from_contract(incident_payload)
        except (KeyError, TypeError, ValueError):
            continue
        incidents[incident.incident_id] = incident
        explanation_payload = response.get("explanation")
        if not isinstance(explanation_payload, Mapping):
            failures[incident.incident_id] = "ExplanationBundle is unavailable from the incident API response."
            continue
        try:
            bundle = ExplanationBundle.from_contract(explanation_payload)
        except (KeyError, TypeError, ValueError):
            failures[incident.incident_id] = "ExplanationBundle from the incident API response is invalid."
            continue
        if bundle.incident_id != incident.incident_id:
            failures[incident.incident_id] = "ExplanationBundle incident_id did not match the incident API response."
            continue
        bundles[incident.incident_id] = bundle
    return resolve_transaction_grounding(
        transaction_id,
        transaction_records,
        incidents,
        bundles,
        failures,
    )


def _incident_map(incidents: Mapping[str, Incident] | Iterable[Incident]) -> dict[str, Incident]:
    if isinstance(incidents, Mapping):
        return {str(key): value for key, value in incidents.items() if isinstance(value, Incident)}
    return {incident.incident_id: incident for incident in incidents}


def _as_strings(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(item for item in value if isinstance(item, str))
    return ()
