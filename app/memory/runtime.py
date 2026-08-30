"""Runtime wiring for the Neo4j-backed memory service."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .neo4j_repository import Neo4jIncidentRepository
from .repository import InMemoryIncidentRepository
from .seed import seed_mastercard_d2
from .service import IncidentMemoryService


@dataclass(frozen=True)
class Neo4jSettings:
    uri: str
    user: str
    password: str
    database: str = "neo4j"

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "Neo4jSettings":
        values = environment if environment is not None else os.environ
        password = values.get("NEO4J_PASSWORD")
        if not password:
            raise RuntimeError("NEO4J_PASSWORD must be set before creating the memory runtime.")
        return cls(
            uri=values.get("NEO4J_URI", "bolt://localhost:7687"),
            user=values.get("NEO4J_USER", "neo4j"),
            password=password,
            database=values.get("NEO4J_DATABASE", "neo4j"),
        )


@dataclass
class MemoryRuntime:
    service: IncidentMemoryService
    driver: Any

    def close(self) -> None:
        self.driver.close()


def create_memory_runtime(
    settings: Neo4jSettings | None = None,
    *,
    driver_factory: Callable[[str, tuple[str, str]], Any] | None = None,
) -> MemoryRuntime:
    """Build the real Neo4j primary repository plus a deterministic fallback."""
    resolved = settings or Neo4jSettings.from_environment()
    if driver_factory is None:
        try:
            from neo4j import GraphDatabase
        except ImportError as error:
            raise RuntimeError("Install the optional Neo4j driver: pip install '.[neo4j]'") from error
        driver_factory = GraphDatabase.driver

    driver = driver_factory(resolved.uri, auth=(resolved.user, resolved.password))
    fallback = InMemoryIncidentRepository()
    seed_mastercard_d2(fallback)
    service = IncidentMemoryService(
        Neo4jIncidentRepository(driver, database=resolved.database),
        fallback=fallback,
    )
    return MemoryRuntime(service=service, driver=driver)
