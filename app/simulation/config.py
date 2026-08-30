"""Versioned, deterministic configuration for the synthetic generator."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isclose
from pathlib import Path
from typing import Any, Mapping


class ConfigurationError(ValueError):
    """Raised when a generator configuration violates its invariants."""


@dataclass(frozen=True)
class WeightedValue:
    identifier: str
    probability: float


@dataclass(frozen=True)
class LatencyProfile:
    """Provider timing parameters for deterministic synthetic attempts."""

    p50_ms: int
    p95_ms: int
    timeout_multiplier: float
    orchestrator_min_ms: int
    orchestrator_max_ms: int

    def validate(self, provider_id: str) -> None:
        if self.p50_ms <= 0 or self.p95_ms < self.p50_ms:
            raise ConfigurationError(f"latency profile {provider_id} must have 0 < p50_ms <= p95_ms")
        if self.timeout_multiplier <= 1:
            raise ConfigurationError(f"latency profile {provider_id} timeout_multiplier must be greater than 1")
        if self.orchestrator_min_ms < 0 or self.orchestrator_max_ms < self.orchestrator_min_ms:
            raise ConfigurationError(f"latency profile {provider_id} has invalid orchestrator bounds")


@dataclass(frozen=True)
class DeclineCode:
    normalized_code: str
    category: str
    retryability: str
    raw_code: str
    raw_message: str
    statuses: tuple[str, ...]
    probability: float

    def validate(self, provider_id: str) -> None:
        if not all(isinstance(value, str) and value for value in self.__dict__.values() if isinstance(value, str)):
            raise ConfigurationError(f"decline profile {provider_id} contains an empty code field")
        if not self.statuses or any(status not in {"DECLINED", "TIMEOUT", "ERROR"} for status in self.statuses):
            raise ConfigurationError(f"decline profile {provider_id} contains an invalid status")
        if not 0 < self.probability <= 1:
            raise ConfigurationError(f"decline profile {provider_id} has an invalid probability")

    def as_payload(self) -> dict[str, str]:
        return {
            "normalized_code": self.normalized_code,
            "category": self.category,
            "retryability": self.retryability,
            "raw_code": self.raw_code,
            "raw_message": self.raw_message,
            "mapping_version": "generator-v1",
        }


@dataclass(frozen=True)
class Distribution:
    dimension: str
    cardinality: int
    values: tuple[WeightedValue, ...]

    def validate(self) -> None:
        if not isinstance(self.cardinality, int) or isinstance(self.cardinality, bool) or self.cardinality <= 0:
            raise ConfigurationError(f"{self.dimension} cardinality must be a positive integer")
        if self.cardinality != len(self.values):
            raise ConfigurationError(
                f"{self.dimension} declares cardinality {self.cardinality}, "
                f"but contains {len(self.values)} values"
            )
        identifiers = [value.identifier for value in self.values]
        if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
            raise ConfigurationError(f"{self.dimension} value identifiers must be non-empty strings")
        if len(set(identifiers)) != len(identifiers):
            raise ConfigurationError(f"{self.dimension} contains duplicate value identifiers")
        if any(isinstance(value.probability, bool) or not isinstance(value.probability, (int, float)) for value in self.values):
            raise ConfigurationError(f"{self.dimension} probabilities must be numeric")
        if any(value.probability < 0 or value.probability > 1 for value in self.values):
            raise ConfigurationError(f"{self.dimension} probabilities must be between 0 and 1")
        if not isclose(sum(value.probability for value in self.values), 1.0, abs_tol=1e-9):
            raise ConfigurationError(f"{self.dimension} probabilities must sum to 1")

    def contains(self, identifier: str) -> bool:
        return any(value.identifier == identifier for value in self.values)


@dataclass(frozen=True)
class ConditionalDistribution:
    rule_id: str
    when: Mapping[str, str]
    target_dimension: str
    values: tuple[WeightedValue, ...]

    def matches(self, context: Mapping[str, str]) -> bool:
        return all(context.get(dimension) == value for dimension, value in self.when.items())


@dataclass(frozen=True)
class ScenarioContractReference:
    schema_version: str
    schema_path: str


@dataclass(frozen=True)
class GeneratorConfig:
    config_version: str
    seed: int
    logical_attempts: int
    days: int
    low_sample_attempts: int
    scenario_contract: ScenarioContractReference
    sampling_order: tuple[str, ...]
    dimensions: Mapping[str, Distribution]
    conditional_probabilities: tuple[ConditionalDistribution, ...]
    latency_profiles: Mapping[str, LatencyProfile]
    decline_profiles: Mapping[str, tuple[DeclineCode, ...]]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "GeneratorConfig":
        try:
            dimensions = {
                name: Distribution(
                    dimension=name,
                    cardinality=definition["cardinality"],
                    values=_weighted_values(definition["values"]),
                )
                for name, definition in payload["dimensions"].items()
            }
            conditional_probabilities = tuple(
                ConditionalDistribution(
                    rule_id=rule["rule_id"],
                    when=dict(rule["when"]),
                    target_dimension=rule["target_dimension"],
                    values=_weighted_values(rule["values"]),
                )
                for rule in payload["conditional_probabilities"]
            )
            scenario_contract = ScenarioContractReference(**payload["scenario_contract"])
            config = cls(
                config_version=payload["config_version"],
                seed=payload["seed"],
                logical_attempts=payload["volume"]["logical_attempts"],
                days=payload["volume"]["days"],
                low_sample_attempts=payload["volume"]["low_sample_attempts"],
                scenario_contract=scenario_contract,
                sampling_order=tuple(payload["sampling_order"]),
                dimensions=dimensions,
                conditional_probabilities=conditional_probabilities,
                latency_profiles={
                    provider: LatencyProfile(**profile) for provider, profile in payload["latency_profiles"].items()
                },
                decline_profiles={
                    provider: tuple(
                        DeclineCode(
                            normalized_code=code["normalized_code"],
                            category=code["category"],
                            retryability=code["retryability"],
                            raw_code=code["raw_code"],
                            raw_message=code["raw_message"],
                            statuses=tuple(code["statuses"]),
                            probability=code["probability"],
                        )
                        for code in profile
                    )
                    for provider, profile in payload["decline_profiles"].items()
                },
            )
        except (KeyError, TypeError) as error:
            raise ConfigurationError(f"Invalid generator configuration shape: {error}") from error
        config.validate()
        return config

    def validate(self) -> None:
        if self.config_version != "1.0":
            raise ConfigurationError("Unsupported generator config version")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool) or self.seed < 0:
            raise ConfigurationError("seed must be a non-negative integer")
        if not isinstance(self.logical_attempts, int) or isinstance(self.logical_attempts, bool) or self.logical_attempts < 100_000_000:
            raise ConfigurationError("logical_attempts must represent hundreds of millions of attempts")
        if not isinstance(self.days, int) or isinstance(self.days, bool) or self.days <= 0:
            raise ConfigurationError("days must be positive")
        if (
            not isinstance(self.low_sample_attempts, int)
            or isinstance(self.low_sample_attempts, bool)
            or not 0 < self.low_sample_attempts < self.logical_attempts
        ):
            raise ConfigurationError("low_sample_attempts must be positive and lower than logical_attempts")
        if (
            not isinstance(self.scenario_contract.schema_path, str)
            or not self.scenario_contract.schema_path
            or self.scenario_contract.schema_version != "1.0"
        ):
            raise ConfigurationError("CTR-SCN-001 v1 reference is required")
        if len(self.sampling_order) != len(set(self.sampling_order)):
            raise ConfigurationError("sampling_order must not repeat dimensions")
        if set(self.sampling_order) != set(self.dimensions):
            raise ConfigurationError("sampling_order must contain every configured dimension exactly once")
        for distribution in self.dimensions.values():
            distribution.validate()
        rule_ids = [rule.rule_id for rule in self.conditional_probabilities]
        if len(set(rule_ids)) != len(rule_ids):
            raise ConfigurationError("conditional rule IDs must be unique")
        for rule in self.conditional_probabilities:
            self._validate_rule(rule)
        self._validate_rule_ambiguity()
        if "default" not in self.latency_profiles or "default" not in self.decline_profiles:
            raise ConfigurationError("latency_profiles and decline_profiles require a default fallback")
        for provider, profile in self.latency_profiles.items():
            profile.validate(provider)
        for provider, codes in self.decline_profiles.items():
            if not codes:
                raise ConfigurationError(f"decline profile {provider} must contain at least one code")
            for code in codes:
                code.validate(provider)
            for status in {status for code in codes for status in code.statuses}:
                if not isclose(sum(code.probability for code in codes if status in code.statuses), 1.0, abs_tol=1e-9):
                    raise ConfigurationError(f"decline profile {provider} probabilities for {status} must sum to 1")

    def distribution_for(self, dimension: str, context: Mapping[str, str]) -> tuple[WeightedValue, ...]:
        matching_rules = [
            rule
            for rule in self.conditional_probabilities
            if rule.target_dimension == dimension and rule.matches(context)
        ]
        if matching_rules:
            return max(matching_rules, key=lambda rule: len(rule.when)).values
        return self.dimensions[dimension].values

    @property
    def fingerprint(self) -> str:
        payload = {
            "config_version": self.config_version,
            "seed": self.seed,
            "logical_attempts": self.logical_attempts,
            "days": self.days,
            "low_sample_attempts": self.low_sample_attempts,
            "scenario_contract": self.scenario_contract.__dict__,
            "sampling_order": self.sampling_order,
            "dimensions": {
                name: {"cardinality": item.cardinality, "values": [value.__dict__ for value in item.values]}
                for name, item in sorted(self.dimensions.items())
            },
            "conditional_probabilities": [
                {
                    "rule_id": rule.rule_id,
                    "when": dict(sorted(rule.when.items())),
                    "target_dimension": rule.target_dimension,
                    "values": [value.__dict__ for value in rule.values],
                }
                for rule in self.conditional_probabilities
            ],
            "latency_profiles": {provider: profile.__dict__ for provider, profile in sorted(self.latency_profiles.items())},
            "decline_profiles": {
                provider: [code.__dict__ for code in codes] for provider, codes in sorted(self.decline_profiles.items())
            },
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return sha256(canonical.encode("utf-8")).hexdigest()

    def latency_profile_for(self, provider_id: str) -> LatencyProfile:
        return self.latency_profiles.get(provider_id, self.latency_profiles["default"])

    def decline_codes_for(self, provider_id: str, status: str) -> tuple[DeclineCode, ...]:
        codes = self.decline_profiles.get(provider_id, self.decline_profiles["default"])
        return tuple(code for code in codes if status in code.statuses)

    def _validate_rule(self, rule: ConditionalDistribution) -> None:
        if not isinstance(rule.rule_id, str) or not rule.rule_id:
            raise ConfigurationError("conditional rule IDs must be non-empty strings")
        if not rule.when:
            raise ConfigurationError(f"Rule {rule.rule_id} must contain a condition")
        if rule.target_dimension not in self.dimensions:
            raise ConfigurationError(f"Rule {rule.rule_id} targets an unknown dimension")
        if rule.target_dimension in rule.when:
            raise ConfigurationError(f"Rule {rule.rule_id} cannot condition on its own target dimension")
        for dimension, identifier in rule.when.items():
            if (
                not isinstance(dimension, str)
                or not isinstance(identifier, str)
                or dimension not in self.dimensions
                or not self.dimensions[dimension].contains(identifier)
            ):
                raise ConfigurationError(f"Rule {rule.rule_id} references an unknown condition value")
        expected = self.dimensions[rule.target_dimension]
        distribution = Distribution(rule.target_dimension, expected.cardinality, rule.values)
        distribution.validate()
        if {value.identifier for value in rule.values} != {value.identifier for value in expected.values}:
            raise ConfigurationError(f"Rule {rule.rule_id} must define every {rule.target_dimension} value")

    def _validate_rule_ambiguity(self) -> None:
        for index, rule in enumerate(self.conditional_probabilities):
            for other in self.conditional_probabilities[index + 1 :]:
                if rule.target_dimension != other.target_dimension:
                    continue
                compatible = all(
                    rule.when.get(dimension, identifier) == identifier
                    for dimension, identifier in other.when.items()
                    if dimension in rule.when
                )
                if compatible and len(rule.when) == len(other.when):
                    raise ConfigurationError(f"Rules {rule.rule_id} and {other.rule_id} are ambiguous")


def load_generator_config(path: Path) -> GeneratorConfig:
    """Load a versioned JSON configuration without generating event data."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    return GeneratorConfig.from_mapping(payload)


def _weighted_values(values: list[Mapping[str, Any]]) -> tuple[WeightedValue, ...]:
    return tuple(WeightedValue(identifier=item["id"], probability=item["probability"]) for item in values)
