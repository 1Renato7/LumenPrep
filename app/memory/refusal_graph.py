"""Versioned refusal-code catalogue and incident links for Neo4j."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from app.refusal_codes.catalog import catalog_rows


@dataclass(frozen=True)
class RefusalGraphSyncResult:
    catalog_rows: int
    incident_links: int


def sync_refusal_catalog(driver: Any, *, database: str = "neo4j") -> int:
    """Upsert immutable, source-versioned mapping nodes without touching incidents."""
    rows = [dict(row, active=True) for row in catalog_rows()]
    with driver.session(database=database) as session:
        _write(session, _UPSERT_CATALOG, {"rows": rows})
    return len(rows)


def backfill_refusal_code_links(driver: Any, *, database: str = "neo4j") -> int:
    """Attach existing Incident nodes to matching catalog facts, replay-safely.

    Historic graphs used either a raw response code (``05``) or a previous
    normalized value.  Matching both is intentional; the edge records which
    representation was observed so a query never needs to guess.
    """
    with driver.session(database=database) as session:
        result = session.run(_SELECT_INCIDENT_CODES)
        records = result.data() if hasattr(result, "data") else (
            [record.data() if hasattr(record, "data") else dict(record) for record in result]
            if hasattr(result, "__iter__") else []
        )
    links = [
        link
        for record in records
        for link in _links_for_incident(record, catalog_rows())
    ]
    if not links:
        return 0
    with driver.session(database=database) as session:
        for chunk in _chunks(links, 500):
            _write(session, _UPSERT_INCIDENT_LINKS, {"links": chunk})
    return len(links)


def sync_and_backfill_refusal_graph(driver: Any, *, database: str = "neo4j") -> RefusalGraphSyncResult:
    return RefusalGraphSyncResult(
        catalog_rows=sync_refusal_catalog(driver, database=database),
        incident_links=backfill_refusal_code_links(driver, database=database),
    )


def _links_for_incident(record: dict[str, Any], rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    try:
        scope = json.loads(str(record.get("scope_json") or "{}"))
        metrics = json.loads(str(record.get("metrics_json") or "{}"))
    except (TypeError, json.JSONDecodeError):
        return []
    providers = {str(value).strip().upper() for value in scope.get("provider_id", []) if str(value).strip()}
    brands = {str(value).strip().upper() for value in scope.get("card_brand", []) if str(value).strip()}
    if not providers:
        return []
    observed_codes = {str(value).strip().upper() for value in metrics.get("decline_codes", []) if str(value).strip()}
    incident_id = str(record.get("incident_id") or "").strip()
    if not incident_id or not observed_codes:
        return []

    links: list[dict[str, str]] = []
    for mapping in rows:
        if mapping["provider_id"] not in providers:
            continue
        if mapping["card_brand"] != "*" and mapping["card_brand"] not in brands:
            continue
        for observed_code in observed_codes:
            if observed_code == mapping["response_code"]:
                links.append({"incident_id": incident_id, "mapping_id": mapping["mapping_id"],
                              "observed_code": observed_code, "match_type": "RAW_RESPONSE_CODE"})
            elif observed_code == mapping["normalized_code"]:
                links.append({"incident_id": incident_id, "mapping_id": mapping["mapping_id"],
                              "observed_code": observed_code, "match_type": "NORMALIZED_CODE"})
    return links


def _chunks(values: list[dict[str, str]], size: int) -> Iterable[list[dict[str, str]]]:
    for index in range(0, len(values), size):
        yield values[index:index + size]


def _write(session: Any, query: str, parameters: dict[str, object]) -> None:
    def write(tx: Any) -> None:
        tx.run(query, **parameters).consume()

    if hasattr(session, "execute_write"):
        session.execute_write(write)
    else:
        session.run(query, **parameters).consume()


_UPSERT_CATALOG = """
UNWIND $rows AS row
MERGE (code:RefusalCode {mapping_id: row.mapping_id})
SET code.provider_id = row.provider_id,
    code.issuer_bank = row.issuer_bank,
    code.card_brand = row.card_brand,
    code.response_code = row.response_code,
    code.normalized_code = row.normalized_code,
    code.outcome = row.outcome,
    code.reason = row.reason,
    code.source = row.source,
    code.mapping_version = row.mapping_version,
    code.active = row.active
"""

_SELECT_INCIDENT_CODES = """
MATCH (incident:Incident)
RETURN incident.incident_id AS incident_id,
       incident.scope_json AS scope_json,
       incident.metrics_json AS metrics_json
"""

_UPSERT_INCIDENT_LINKS = """
UNWIND $links AS link
MATCH (incident:Incident {incident_id: link.incident_id})
MATCH (code:RefusalCode {mapping_id: link.mapping_id})
MERGE (incident)-[observation:OBSERVED_REFUSAL_CODE {
  mapping_id: link.mapping_id,
  observed_code: link.observed_code
}]->(code)
SET observation.match_type = link.match_type,
    observation.catalog_source = code.source,
    observation.mapping_version = code.mapping_version
"""
