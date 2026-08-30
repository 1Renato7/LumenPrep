"""Initialize the local Neo4j graph and seed the deterministic precedent."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .neo4j_repository import Neo4jIncidentRepository
from .seed import seed_mastercard_d2

_ROOT = Path(__file__).resolve().parents[2]
_CONSTRAINTS_FILE = _ROOT / "graph" / "constraints.cypher"


def _statements(cypher_file: Path | str = _CONSTRAINTS_FILE) -> tuple[str, ...]:
    """Return executable Cypher statements, ignoring comments and blank lines."""
    content = "\n".join(
        line
        for line in Path(cypher_file).read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("//")
    )
    return tuple(statement.strip() for statement in content.split(";") if statement.strip())


def _environment() -> tuple[str, str, str, str]:
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    if not password:
        raise RuntimeError("NEO4J_PASSWORD is required; load it from .env.docker before bootstrapping.")
    return uri, user, password, database


def bootstrap(*, driver: Any, database: str = "neo4j") -> str:
    """Apply replay-safe constraints and upsert the required D-2 precedent."""
    with driver.session(database=database) as session:
        for statement in _statements():
            session.run(statement).consume()
    repository = Neo4jIncidentRepository(driver, database=database)
    return seed_mastercard_d2(repository).incident_id


def main() -> None:
    try:
        from neo4j import GraphDatabase
    except ImportError as error:
        raise RuntimeError("Install the optional driver with: pip install '.[neo4j]'") from error

    uri, user, password, database = _environment()
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        driver.verify_connectivity()
        incident_id = bootstrap(driver=driver, database=database)
    finally:
        driver.close()
    print(f"Neo4j initialized; seeded {incident_id}.")


if __name__ == "__main__":
    main()
