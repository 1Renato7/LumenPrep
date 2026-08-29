"""Grounded links from transaction records to an already-derived Incident."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from app.memory.models import Incident


@dataclass(frozen=True)
class TransactionEvidenceTrace:
    """Authorized transaction evidence for one Incident, in stable order."""

    incident_id: str
    transaction_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


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


def _as_strings(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(item for item in value if isinstance(item, str))
    return ()
