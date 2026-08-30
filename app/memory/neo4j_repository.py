"""Neo4j adapter with injected driver, idempotent writes, and no hard dependency."""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime
from typing import Any

from .models import HistoricalIncident, Incident


class Neo4jIncidentRepository:
    """Driver adapter; callers fall back when this adapter raises or is unhealthy."""

    def __init__(
        self,
        driver: Any,
        *,
        database: str = "neo4j",
        timeout_seconds: float = 2.0,
        include_evaluation: bool = False,
    ) -> None:
        self.driver = driver
        self.database = database
        self.timeout_seconds = timeout_seconds
        self.include_evaluation = include_evaluation

    def health(self) -> bool:
        try:
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1 AS healthy", timeout=self.timeout_seconds).single()
            return True
        except Exception:
            return False

    def upsert(self, incident: HistoricalIncident) -> None:
        parameters = {
            "incident_id": incident.incident_id,
            "occurred_at": incident.occurred_at.isoformat(),
            "scope_json": json.dumps(incident.scope, sort_keys=True),
            "scope_values": sorted({value for values in incident.scope.values() for value in values}),
            "metrics_json": json.dumps(incident.metrics, sort_keys=True),
            "confirmation": incident.confirmation,
            "confirmed_cause": incident.confirmed_cause,
            "prior_playbook_id": incident.prior_playbook_id,
            "evidence_ids": list(incident.evidence_ids),
            "provenance": incident.provenance,
            "providers": list(incident.scope.get("provider_id", ())),
            "countries": list(incident.scope.get("country", ())),
            "brands": list(incident.scope.get("card_brand", ())),
        }
        with self.driver.session(database=self.database) as session:
            self._write(session, parameters)

    def confirmed_incidents(self, query: Incident | None = None) -> Iterable[HistoricalIncident]:
        query_values = sorted({value for values in (query.scope.values() if query else ()) for value in values})
        with self.driver.session(database=self.database) as session:
            result = session.run(
                _SELECT_CONFIRMED,
                query_scope_values=query_values,
                include_evaluation=self.include_evaluation,
                timeout=self.timeout_seconds,
            )
            return tuple(_to_historical(record.data() if hasattr(record, "data") else dict(record)) for record in result)

    def _write(self, session: Any, parameters: dict[str, object]) -> None:
        def write(tx: Any) -> None:
            tx.run(_UPSERT, timeout=self.timeout_seconds, **parameters).consume()

        if hasattr(session, "execute_write"):
            session.execute_write(write)
        else:
            session.run(_UPSERT, timeout=self.timeout_seconds, **parameters).consume()


def _to_historical(row: dict[str, object]) -> HistoricalIncident:
    return HistoricalIncident(
        incident_id=str(row["incident_id"]),
        occurred_at=datetime.fromisoformat(str(row["occurred_at"]).replace("Z", "+00:00")),
        scope={key: tuple(values) for key, values in json.loads(str(row["scope_json"])).items()},
        metrics=json.loads(str(row["metrics_json"])),
        confirmation=str(row["confirmation"]),
        confirmed_cause=str(row["confirmed_cause"]),
        prior_playbook_id=str(row["prior_playbook_id"]),
        evidence_ids=tuple(row["evidence_ids"]),
        provenance=str(row.get("provenance") or "REAL_HUMAN_REVIEW"),
    )


_UPSERT = """
MERGE (incident:Incident {incident_id: $incident_id})
SET incident.occurred_at = $occurred_at,
    incident.scope_json = $scope_json,
    incident.scope_values = $scope_values,
    incident.metrics_json = $metrics_json,
    incident.confirmation = $confirmation,
    incident.confirmed_cause = $confirmed_cause,
    incident.prior_playbook_id = $prior_playbook_id,
    incident.evidence_ids = $evidence_ids,
    incident.provenance = $provenance
MERGE (cause:Cause {cause_id: $confirmed_cause})
MERGE (incident)-[:CONFIRMED_AS]->(cause)
MERGE (playbook:Playbook {playbook_id: $prior_playbook_id})
MERGE (incident)-[:RESOLVED_WITH]->(playbook)
FOREACH (provider_id IN $providers |
  MERGE (provider:Provider {provider_id: provider_id})
  MERGE (incident)-[:AFFECTED]->(provider))
FOREACH (country_code IN $countries |
  MERGE (country:Country {code: country_code})
  MERGE (incident)-[:AFFECTED]->(country))
FOREACH (brand_name IN $brands |
  MERGE (brand:CardBrand {name: brand_name})
  MERGE (incident)-[:AFFECTED]->(brand))
FOREACH (evidence_id IN $evidence_ids |
  MERGE (evidence:Evidence {evidence_id: evidence_id})
  MERGE (incident)-[:HAS_EVIDENCE]->(evidence))
"""

_SELECT_CONFIRMED = """
MATCH (incident:Incident)
WHERE (incident.confirmation = 'HUMAN_CONFIRMED'
       OR ($include_evaluation AND incident.confirmation = 'EVALUATION_CONFIRMED'))
  AND ($query_scope_values = [] OR any(value IN $query_scope_values WHERE value IN incident.scope_values))
RETURN incident.incident_id AS incident_id,
       incident.occurred_at AS occurred_at,
       incident.scope_json AS scope_json,
       incident.metrics_json AS metrics_json,
       incident.confirmation AS confirmation,
       incident.confirmed_cause AS confirmed_cause,
       incident.prior_playbook_id AS prior_playbook_id,
       incident.evidence_ids AS evidence_ids,
       incident.provenance AS provenance
ORDER BY incident.occurred_at DESC, incident.incident_id ASC
"""

