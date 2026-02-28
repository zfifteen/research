from __future__ import annotations

import numpy as np

from phasewall_poc.config import ScenarioConfig
from phasewall_poc.sim_optimizers import run_optimizer_scenario
from phasewall_poc.sim_walkers import run_walker_scenario


def test_walker_reproducible() -> None:
    cfg = ScenarioConfig(
        name="walker_test",
        dim=2,
        noise_std=0.25,
        steps_or_evals=80,
        seeds=[11, 12],
        phasewall_strength=0.4,
        engine="walker",
        n_agents=80,
    )
    a = run_walker_scenario(cfg)
    b = run_walker_scenario(cfg)
    assert [x.score for x in a] == [x.score for x in b]


def test_optimizer_reproducible() -> None:
    cfg = ScenarioConfig(
        name="opt_test",
        dim=10,
        noise_std=0.1,
        steps_or_evals=600,
        seeds=[3, 4],
        phasewall_strength=0.4,
        engine="toy_es",
        objective="sphere",
        population_size=20,
    )
    a = run_optimizer_scenario(cfg)
    b = run_optimizer_scenario(cfg)
    assert [x.score for x in a] == [x.score for x in b]


def test_phasewall_reduces_or_matches_walker_escape_rate() -> None:
    cfg = ScenarioConfig(
        name="walker_escape",
        dim=2,
        noise_std=0.30,
        steps_or_evals=100,
        seeds=[20, 21, 22, 23],
        phasewall_strength=0.4,
        engine="walker",
        n_agents=120,
    )
    rows = run_walker_scenario(cfg)
    vanilla = [r.metrics["escape_rate"] for r in rows if r.method == "vanilla"]
    phase = [r.metrics["escape_rate"] for r in rows if r.method == "phasewall"]
    assert float(np.mean(phase)) <= float(np.mean(vanilla))


def test_deterministic_no_noise_not_degraded_for_sphere() -> None:
    cfg = ScenarioConfig(
        name="deterministic_sphere",
        dim=10,
        noise_std=0.0,
        steps_or_evals=800,
        seeds=[1, 2, 3],
        phasewall_strength=0.4,
        engine="cmaes_style",
        objective="sphere",
        population_size=24,
    )
    rows = run_optimizer_scenario(cfg)
    vanilla = np.array([r.score for r in rows if r.method == "vanilla"])
    phase = np.array([r.score for r in rows if r.method == "phasewall"])
    assert float(np.median(phase)) <= float(np.median(vanilla)) + 1e-10
