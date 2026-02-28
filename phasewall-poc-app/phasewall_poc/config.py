from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np


DEFAULT_PHASEWALL_STRENGTH = 0.4
DEFAULT_SIGMA = 1.0


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    dim: int
    noise_std: float
    steps_or_evals: int
    seeds: list[int]
    phasewall_strength: float
    engine: str
    objective: str = "sphere"
    population_size: int = 24
    n_agents: int = 120
    sigma: float = DEFAULT_SIGMA

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunResult:
    scenario: str
    engine: str
    method: str
    seed: int
    score: float
    metrics: dict[str, float]


@dataclass(frozen=True)
class AggregateResult:
    scenario: str
    engine: str
    method: str
    n: int
    median_score: float
    mean_score: float
    std_score: float
    ci_low: float
    ci_high: float
    win_rate: float
    ratio_vs_vanilla: float
    wilcoxon_p: float


OBJECTIVES = ("sphere", "rosenbrock", "rastrigin")
ENGINES = ("walker", "toy_es", "cmaes_style")


def make_seed_list(seed_count: int, base_seed: int = 0) -> list[int]:
    return [base_seed + i for i in range(seed_count)]


def core_benchmark_scenarios(seed_count: int = 20) -> list[ScenarioConfig]:
    seeds = make_seed_list(seed_count, base_seed=100)
    out: list[ScenarioConfig] = []

    out.append(
        ScenarioConfig(
            name="walker_2d_noisy",
            dim=2,
            noise_std=0.25,
            steps_or_evals=120,
            seeds=seeds,
            phasewall_strength=DEFAULT_PHASEWALL_STRENGTH,
            engine="walker",
            objective="sphere",
            n_agents=140,
        )
    )

    for dim in (2, 10):
        for objective in OBJECTIVES:
            out.append(
                ScenarioConfig(
                    name=f"toy_es_{objective}_{dim}d",
                    dim=dim,
                    noise_std=0.1,
                    steps_or_evals=1200,
                    seeds=seeds,
                    phasewall_strength=DEFAULT_PHASEWALL_STRENGTH,
                    engine="toy_es",
                    objective=objective,
                    population_size=24,
                )
            )
            out.append(
                ScenarioConfig(
                    name=f"cmaes_style_{objective}_{dim}d",
                    dim=dim,
                    noise_std=0.1,
                    steps_or_evals=1200,
                    seeds=seeds,
                    phasewall_strength=DEFAULT_PHASEWALL_STRENGTH,
                    engine="cmaes_style",
                    objective=objective,
                    population_size=24,
                )
            )

    return out


def set_global_seed(seed: int) -> np.random.Generator:
    np.random.seed(seed)
    return np.random.default_rng(seed)
