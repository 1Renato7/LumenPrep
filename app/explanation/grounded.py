"""Deterministic fallback for CTR-LLM-001 with evidence validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from app.memory.models import Incident, MemoryStatus, SimilarIncidentResult


@dataclass(frozen=True)
class Playbook:
    playbook_id: str
    cause_categories: frozenset[str]
    required_scope: dict[str, frozenset[str]]
    action: str
    cautions: tuple[str, ...]

    def applies_to(self, incident: Incident) -> bool:
        if incident.root_cause_status != "SUPPORTED":
            return False
        if incident.root_cause_category not in self.cause_categories:
            return False
        return all(required <= set(incident.scope.get(key, ())) for key, required in self.required_scope.items())


@dataclass(frozen=True)
class ExplanationBundle:
    incident_id: str
    executive_summary: str
    operations_summary: str
    what_happened: str
    where_and_why: str
    recurrence_statement: str | None
    evidence_ids: tuple[str, ...]
    playbook_id: str
    recommended_action: str
    limitations: tuple[str, ...]
    model_version: str = "deterministic-template"

    @classmethod
    def from_contract(cls, payload: Mapping[str, object]) -> "ExplanationBundle":
        """Read the existing CTR-LLM-001 shape without starting a model call."""

        if payload.get("execution") != "HUMAN_ONLY":
            raise ValueError("ExplanationBundle execution must be HUMAN_ONLY")
        incident_id = payload.get("incident_id")
        if not isinstance(incident_id, str) or not incident_id:
            raise ValueError("ExplanationBundle incident_id must be a non-empty string")
        required_text = (
            "executive_summary",
            "operations_summary",
            "what_happened",
            "where_and_why",
            "playbook_id",
            "recommended_action",
        )
        if any(not isinstance(payload.get(field), str) for field in required_text):
            raise ValueError("ExplanationBundle is missing required text fields")
        recurrence_statement = payload.get("recurrence_statement")
        if recurrence_statement is not None and not isinstance(recurrence_statement, str):
            raise ValueError("ExplanationBundle recurrence_statement must be a string or null")
        evidence_ids = payload.get("evidence_ids")
        limitations = payload.get("limitations")
        if not isinstance(evidence_ids, list) or not all(isinstance(item, str) for item in evidence_ids):
            raise ValueError("ExplanationBundle evidence_ids must be a list of strings")
        if not isinstance(limitations, list) or not all(isinstance(item, str) for item in limitations):
            raise ValueError("ExplanationBundle limitations must be a list of strings")
        model_version = payload.get("model_version", "deterministic-template")
        if not isinstance(model_version, str):
            raise ValueError("ExplanationBundle model_version must be a string")
        return cls(
            incident_id=incident_id,
            executive_summary=str(payload["executive_summary"]),
            operations_summary=str(payload["operations_summary"]),
            what_happened=str(payload["what_happened"]),
            where_and_why=str(payload["where_and_why"]),
            recurrence_statement=recurrence_statement,
            evidence_ids=tuple(evidence_ids),
            playbook_id=str(payload["playbook_id"]),
            recommended_action=str(payload["recommended_action"]),
            limitations=tuple(limitations),
            model_version=model_version,
        )

    def to_contract(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "incident_id": self.incident_id,
            "executive_summary": self.executive_summary,
            "operations_summary": self.operations_summary,
            "what_happened": self.what_happened,
            "where_and_why": self.where_and_why,
            "recurrence_statement": self.recurrence_statement,
            "evidence_ids": list(self.evidence_ids),
            "playbook_id": self.playbook_id,
            "recommended_action": self.recommended_action,
            "execution": "HUMAN_ONLY",
            "limitations": list(self.limitations),
            "model_version": self.model_version,
        }


class GroundedExplainer:
    def __init__(self, playbooks: Iterable[Playbook]) -> None:
        self.playbooks = {playbook.playbook_id: playbook for playbook in playbooks}
        self.playbooks.setdefault(
            "PB-GENERIC-INVESTIGATION",
            Playbook(
                playbook_id="PB-GENERIC-INVESTIGATION",
                cause_categories=frozenset(),
                required_scope={},
                action="Inspect current evidence and escalate to the payment operations owner.",
                cautions=("Do not execute payment actions automatically.",),
            ),
        )

    def explain(self, incident: Incident, memory: SimilarIncidentResult) -> ExplanationBundle:
        evidence_ids = list(incident.evidence_ids)
        current_evidence_available = bool(incident.evidence_ids)
        limitations = ["Recommendation is HUMAN_ONLY; the system does not execute payment actions."]
        recurrence_statement = None
        selected = self._current_playbook(incident) if current_evidence_available else self.playbooks["PB-GENERIC-INVESTIGATION"]

        if memory.memory_status is MemoryStatus.MATCH_FOUND:
            precedent = memory.matches[0]
            evidence_ids.extend(precedent.evidence_ids)
            if current_evidence_available:
                recurrence_statement = (
                    f"Probable recurrence of {precedent.incident_id}; matching factors: "
                    f"{', '.join(precedent.matching_factors)}. Differences: "
                    f"{', '.join(precedent.different_factors) or 'none recorded'}."
                )
            else:
                limitations.append(
                    "A historical precedent was retrieved, but current evidence IDs are absent; recurrence is not asserted."
                )
            prior = self.playbooks.get(precedent.prior_playbook_id)
            if current_evidence_available and prior is not None and prior.applies_to(incident):
                selected = prior
            elif incident.root_cause_status == "INCONCLUSIVE":
                limitations.append(
                    "The current cause remains INCONCLUSIVE; the historical playbook is investigation guidance only."
                )
        elif memory.memory_status is MemoryStatus.NO_PRECEDENT:
            limitations.append("No confirmed historical precedent passed the retrieval threshold.")
        else:
            limitations.append("Incident memory is unavailable; the current causal status is unchanged.")

        if incident.root_cause_status == "SUPPORTED" and current_evidence_available:
            where_and_why = f"Current evidence supports {incident.root_cause_category}."
        elif incident.root_cause_status == "SUPPORTED":
            where_and_why = "The current causal conclusion is withheld because no current evidence IDs are available."
            limitations.append("SUPPORTED status arrived without current evidence IDs; use investigation guidance only.")
        else:
            where_and_why = "The current cause remains INCONCLUSIVE; inspect the stated limitations and evidence."

        bundle = ExplanationBundle(
            incident_id=incident.incident_id,
            executive_summary="Payment incident detected; estimated GMV at risk requires human review.",
            operations_summary="Review the scoped evidence, current diagnosis, and the selected human-only playbook.",
            what_happened="The system observed an incident in the supplied payment scope.",
            where_and_why=where_and_why,
            recurrence_statement=recurrence_statement,
            evidence_ids=tuple(dict.fromkeys(evidence_ids)),
            playbook_id=selected.playbook_id,
            recommended_action=selected.action,
            limitations=tuple(limitations + list(selected.cautions)),
        )
        validate_evidence_ids(bundle, incident, memory)
        return bundle

    def _current_playbook(self, incident: Incident) -> Playbook:
        applicable = [playbook for playbook in self.playbooks.values() if playbook.applies_to(incident)]
        if applicable:
            return applicable[0]
        return self.playbooks["PB-GENERIC-INVESTIGATION"]


def validate_evidence_ids(bundle: ExplanationBundle, incident: Incident, memory: SimilarIncidentResult) -> None:
    allowed = set(incident.evidence_ids)
    for match in memory.matches:
        allowed.update(match.evidence_ids)
    invalid = set(bundle.evidence_ids) - allowed
    if invalid:
        raise ValueError(f"explanation contains unknown evidence IDs: {sorted(invalid)}")

