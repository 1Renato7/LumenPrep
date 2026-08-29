"""Contract and reproducibility tests for TASK-DATA-001 / LUM2-43."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from app.simulation.config import ConfigurationError, GeneratorConfig, load_generator_config
from app.simulation.sampling import DeterministicDimensionSampler
from app.simulation.scenario_contract import ScenarioContractError, ScenarioV1Contract


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "generator" / "v1" / "default.json"
SCENARIO_FIXTURE_PATH = ROOT / "contracts" / "fixtures" / "scenario-provider-br.json"


class GeneratorConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_generator_config(CONFIG_PATH)

    def test_default_config_has_requested_cardinalities_and_scale(self) -> None:
        self.assertEqual(self.config.logical_attempts, 360_000_000)
        self.assertEqual(self.config.days, 90)
        self.assertEqual(self.config.low_sample_attempts, 12)
        self.assertEqual(
            set(self.config.dimensions),
            {"country", "merchant_id", "provider_id", "payment_method_category", "status"},
        )
        self.assertTrue(
            all(
                distribution.cardinality == (4 if name == "status" else 3)
                for name, distribution in self.config.dimensions.items()
            )
        )

    def test_every_distribution_is_normalized(self) -> None:
        for dimension in self.config.dimensions:
            self.assertAlmostEqual(
                sum(value.probability for value in self.config.distribution_for(dimension, {"country": "BR"})),
                1.0,
            )

    def test_same_seed_produces_same_attempt_sequence_and_fingerprint(self) -> None:
        first = DeterministicDimensionSampler(self.config).sample_attempts(20)
        second_config = load_generator_config(CONFIG_PATH)
        second = DeterministicDimensionSampler(second_config).sample_attempts(20)
        self.assertEqual(first, second)
        self.assertEqual(self.config.fingerprint, second_config.fingerprint)

    def test_rejects_probability_distribution_that_is_not_normalized(self) -> None:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        invalid_payload = copy.deepcopy(payload)
        invalid_payload["dimensions"]["country"]["values"][0]["probability"] = 0.7
        with self.assertRaises(ConfigurationError):
            GeneratorConfig.from_mapping(invalid_payload)

    def test_rejects_equally_specific_overlapping_rules(self) -> None:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        invalid_payload = copy.deepcopy(payload)
        invalid_payload["conditional_probabilities"].append(
            {
                "rule_id": "provider-by-merchant",
                "when": {"merchant_id": "merchant_aurora"},
                "target_dimension": "provider_id",
                "values": [
                    {"id": "stripe", "probability": 0.4},
                    {"id": "adyen", "probability": 0.3},
                    {"id": "dlocal", "probability": 0.3},
                ],
            }
        )
        with self.assertRaises(ConfigurationError):
            GeneratorConfig.from_mapping(invalid_payload)


class ScenarioContractTest(unittest.TestCase):
    def setUp(self) -> None:
        config = load_generator_config(CONFIG_PATH)
        self.contract = ScenarioV1Contract(ROOT / config.scenario_contract.schema_path)
        self.fixture = json.loads(SCENARIO_FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_accepts_fixture_validated_by_task_28(self) -> None:
        scenario = self.contract.parse(self.fixture)
        self.assertEqual(scenario.scenario_id, "scenario_provider_br")
        self.assertEqual(scenario.filters["country"], ("BR",))

    def test_rejects_missing_required_or_ground_truth_fields(self) -> None:
        missing_seed = dict(self.fixture)
        del missing_seed["seed"]
        with self.assertRaises(ScenarioContractError):
            self.contract.parse(missing_seed)
        with_ground_truth = dict(self.fixture, ground_truth={"root_cause": "hidden"})
        with self.assertRaises(ScenarioContractError):
            self.contract.parse(with_ground_truth)

    def test_matches_schema_permitted_empty_filters_and_rejects_invalid_time(self) -> None:
        global_scenario = dict(self.fixture, filters={})
        self.assertEqual(self.contract.parse(global_scenario).filters, {})
        invalid_time = dict(self.fixture, start_at="2026-08-29T14:03:00")
        with self.assertRaises(ScenarioContractError):
            self.contract.parse(invalid_time)
