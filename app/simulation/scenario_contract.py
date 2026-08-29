"""Boundary adapter for the validated CTR-SCN-001 scenario contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Mapping, Protocol


class ScenarioContractError(ValueError):
    """Raised when a scenario cannot cross the generator contract boundary."""


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_id: str
    seed: int
    filters: Mapping[str, tuple[str, ...]]
    effects: Mapping[str, Any]


class ScenarioContract(Protocol):
    """Replace this adapter when CTR-SCN-001 receives a new version."""

    def parse(self, payload: Mapping[str, Any]) -> ScenarioDefinition: ...


class ScenarioV1Contract:
    """Reads the contract validated in LUM2-28 without owning or mutating it."""

    def __init__(self, schema_path: Path) -> None:
        self._schema = json.loads(schema_path.read_text(encoding="utf-8"))

    def parse(self, payload: Mapping[str, Any]) -> ScenarioDefinition:
        required = set(self._schema["required"])
        missing = required - set(payload)
        if missing:
            raise ScenarioContractError(f"Scenario is missing required fields: {sorted(missing)}")
        if self._schema.get("additionalProperties") is False:
            unexpected = set(payload) - set(self._schema["properties"])
            if unexpected:
                raise ScenarioContractError(f"Scenario has unexpected fields: {sorted(unexpected)}")
        properties = self._schema["properties"]
        if payload["schema_version"] != properties["schema_version"]["const"]:
            raise ScenarioContractError("Scenario schema_version is unsupported")
        if not isinstance(payload["scenario_id"], str) or not payload["scenario_id"]:
            raise ScenarioContractError("scenario_id must be a non-empty string")
        if not _non_negative_integer(payload["seed"]):
            raise ScenarioContractError("seed must be a non-negative integer")
        if not _positive_integer(payload["duration_seconds"]):
            raise ScenarioContractError("duration_seconds must be a positive integer")
        _validate_datetime(payload["start_at"])
        filters = _parse_filters(payload["filters"])
        effects = _parse_effects(payload["effects"], properties["effects"])
        return ScenarioDefinition(
            scenario_id=payload["scenario_id"],
            seed=payload["seed"],
            filters=filters,
            effects=effects,
        )


def _parse_filters(value: Any) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, Mapping):
        raise ScenarioContractError("filters must be an object")
    parsed: dict[str, tuple[str, ...]] = {}
    for dimension, identifiers in value.items():
        if not isinstance(dimension, str) or not isinstance(identifiers, list) or not identifiers:
            raise ScenarioContractError("every filter must contain at least one string identifier")
        if not all(isinstance(identifier, str) for identifier in identifiers):
            raise ScenarioContractError("every filter identifier must be a string")
        parsed[dimension] = tuple(identifiers)
    return parsed


def _parse_effects(value: Any, schema: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or not value:
        raise ScenarioContractError("effects must be a non-empty object")
    allowed = schema["properties"]
    unknown = set(value) - set(allowed)
    if unknown:
        raise ScenarioContractError(f"effects contain unsupported fields: {sorted(unknown)}")
    for effect, effect_value in value.items():
        effect_schema = allowed[effect]
        if effect == "decline_code_distribution":
            _validate_probability_map(effect_value)
        else:
            if isinstance(effect_value, bool) or not isinstance(effect_value, (int, float)):
                raise ScenarioContractError(f"{effect} must be numeric")
            if "minimum" in effect_schema and effect_value < effect_schema["minimum"]:
                raise ScenarioContractError(f"{effect} is below its minimum")
            if "maximum" in effect_schema and effect_value > effect_schema["maximum"]:
                raise ScenarioContractError(f"{effect} is above its maximum")
    return dict(value)


def _validate_probability_map(value: Any) -> None:
    if not isinstance(value, Mapping):
        raise ScenarioContractError("decline_code_distribution must be an object")
    if not all(
        isinstance(code, str)
        and not isinstance(weight, bool)
        and isinstance(weight, (int, float))
        and 0 <= weight <= 1
        for code, weight in value.items()
    ):
        raise ScenarioContractError("decline_code_distribution values must be probabilities")


def _validate_datetime(value: Any) -> None:
    if not isinstance(value, str):
        raise ScenarioContractError("start_at must be an RFC 3339 date-time string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ScenarioContractError("start_at must be an RFC 3339 date-time string") from error
    if parsed.tzinfo is None:
        raise ScenarioContractError("start_at must include a timezone")


def _non_negative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _positive_integer(value: Any) -> bool:
    return _non_negative_integer(value) and value > 0
