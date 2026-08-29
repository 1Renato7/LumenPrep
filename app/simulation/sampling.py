"""Small deterministic sampler used to prove configuration reproducibility."""

from __future__ import annotations

from random import Random

from app.simulation.config import GeneratorConfig, WeightedValue


class DeterministicDimensionSampler:
    """Samples dimensions from a config; it never reads or emits ground truth."""

    def __init__(self, config: GeneratorConfig) -> None:
        self._config = config
        self._random = Random(config.seed)

    def sample_attempt(self) -> dict[str, str]:
        context: dict[str, str] = {}
        for dimension in self._config.sampling_order:
            context[dimension] = _choose(self._random, self._config.distribution_for(dimension, context))
        return context

    def sample_attempts(self, count: int) -> list[dict[str, str]]:
        if count < 0:
            raise ValueError("count must be non-negative")
        return [self.sample_attempt() for _ in range(count)]


def _choose(random: Random, values: tuple[WeightedValue, ...]) -> str:
    threshold = random.random()
    cumulative = 0.0
    for value in values:
        cumulative += value.probability
        if threshold < cumulative:
            return value.identifier
    return values[-1].identifier
