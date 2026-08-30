"""Deterministic checks that bind a displayed transaction result to its source.

The current product intentionally simulates a provider.  In that mode the pure
``adapt_transaction`` result is the authoritative provider result; the raw and
canonical events persisted by ingestion are the durable audit trail.  These
checks compare all three.  They do not ask a language model to decide whether an
error sounds plausible.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.simulation.transaction_outcomes import AdaptedTransaction, adapt_transaction


@dataclass(frozen=True)
class ProvenanceAudit:
    """Verdict for one terminal transaction, with concrete failed invariants."""

    passed: bool
    failures: tuple[str, ...]


def audit_terminal_transaction(
    record: Mapping[str, Any],
    *,
    raw_event: Mapping[str, Any] | None,
    canonical_event: Mapping[str, Any] | None,
    source_input: Mapping[str, Any] | None = None,
) -> ProvenanceAudit:
    """Reject a displayed result that cannot be rebuilt from persisted facts.

    ``related_incident_ids`` may be appended by the incident linker.  It is not a
    transaction failure reason, so the audit only verifies it is a list of stable
    IDs.  All other classification fields must equal the deterministic provider
    adapter output exactly.
    """
    failures: list[str] = []
    transaction_id = record.get("transaction_id")
    correlation_id = record.get("correlation_id")
    transaction_input = source_input or record.get("input")
    if not isinstance(transaction_id, str) or not isinstance(correlation_id, str) or not isinstance(transaction_input, Mapping):
        return ProvenanceAudit(False, ("record is missing transaction_id, correlation_id, or source input",))

    expected = adapt_transaction(
        transaction_input,
        transaction_id=transaction_id,
        correlation_id=correlation_id,
    )
    _check_record(record, expected, failures)
    _check_event("raw_event", raw_event, expected.event, failures)
    _check_event("canonical_event", canonical_event, expected.event, failures)
    return ProvenanceAudit(not failures, tuple(failures))


def _check_record(record: Mapping[str, Any], expected: AdaptedTransaction, failures: list[str]) -> None:
    if record.get("status") != expected.result:
        failures.append(f"status is {record.get('status')!r}, expected {expected.result!r}")
    if record.get("outcome") != expected.outcome:
        failures.append("outcome does not match the deterministic provider result")

    classification = record.get("classification")
    if not isinstance(classification, Mapping):
        failures.append("classification is absent or not an object")
        return
    for key in ("category", "reason", "confidence", "evidence_ids"):
        if classification.get(key) != expected.classification[key]:
            failures.append(f"classification.{key} does not match the provider result")
    unexpected = set(classification) - set(expected.classification)
    if unexpected:
        failures.append(f"classification has unaudited fields: {sorted(unexpected)!r}")
    related = classification.get("related_incident_ids")
    if not isinstance(related, list) or not all(isinstance(item, str) and item for item in related):
        failures.append("classification.related_incident_ids is not a list of stable IDs")


def _check_event(
    name: str,
    actual: Mapping[str, Any] | None,
    expected: Mapping[str, Any],
    failures: list[str],
) -> None:
    if actual is None:
        failures.append(f"{name} is missing")
    elif dict(actual) != dict(expected):
        failures.append(f"{name} does not match the deterministic provider event")
