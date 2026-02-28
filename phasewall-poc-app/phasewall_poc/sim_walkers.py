from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import RunResult, ScenarioConfig
from .geometry import gaussian_gradient
from .phasewall import apply_phase_wall_z, phase_aware_noise


@dataclass
class WalkerTrace:
    trajectories: np.ndarray
    radii: np.ndarray
    escape_rate: float
    inside_fraction: float
    angular_dispersion: float
    score: float


def _init_positions(n_agents: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    vec = rng.normal(size=(n_agents, dim))
    vec /= np.linalg.norm(vec, axis=1, keepdims=True) + 1e-12
    radii = rng.uniform(1.1, 2.5, size=(n_agents, 1))
    return vec * radii


def _simulate(
    *,
    dim: int,
    n_agents: int,
    steps: int,
    noise_std: float,
    seed: int,
    phasewall_enabled: bool,
    phasewall_strength: float,
    sigma: float = 1.0,
) -> WalkerTrace:
    rng = np.random.default_rng(seed)
    positions = _init_positions(n_agents, dim, rng)

    trajectories = np.zeros((steps + 1, n_agents, dim), dtype=float)
    radii = np.zeros((steps + 1, n_agents), dtype=float)
    trajectories[0] = positions
    radii[0] = np.linalg.norm(positions, axis=1)

    escapes = 0
    inside_count = 0
    angle_changes: list[float] = []

    for t in range(1, steps + 1):
        prev = positions.copy()
        grad = gaussian_gradient(positions, sigma=sigma)
        noise = rng.normal(0.0, noise_std, size=positions.shape)

        if phasewall_enabled:
            noise = phase_aware_noise(
                positions,
                noise,
                r0=sigma,
                strength=phasewall_strength,
            )

        step = 0.28 * grad + noise
        positions = positions + step
        if phasewall_enabled:
            positions = apply_phase_wall_z(positions, r0=sigma, strength=1.0)

        prev_r = np.linalg.norm(prev, axis=1)
        curr_r = np.linalg.norm(positions, axis=1)

        escaped = (prev_r <= sigma) & (curr_r > sigma)
        escapes += int(np.sum(escaped))
        inside_count += int(np.sum(prev_r <= sigma))

        prev_ang = np.arctan2(prev[:, 1], prev[:, 0])
        curr_ang = np.arctan2(positions[:, 1], positions[:, 0])
        d_ang = np.unwrap(np.stack([prev_ang, curr_ang], axis=0), axis=0)
        delta = np.abs(d_ang[1] - d_ang[0])
        angle_changes.extend(delta.tolist())

        trajectories[t] = positions
        radii[t] = curr_r

    escape_rate = escapes / max(1, inside_count)
    inside_fraction = float(np.mean(radii[-1] <= sigma))
    angular_dispersion = float(np.std(angle_changes))
    score = float(np.mean(radii[-1]))

    return WalkerTrace(
        trajectories=trajectories,
        radii=radii,
        escape_rate=float(escape_rate),
        inside_fraction=inside_fraction,
        angular_dispersion=angular_dispersion,
        score=score,
    )


def run_walker_pair_demo(
    *,
    dim: int,
    n_agents: int,
    steps: int,
    noise_std: float,
    seed: int,
    phasewall_strength: float,
) -> dict[str, dict[str, np.ndarray | dict[str, float]]]:
    vanilla = _simulate(
        dim=dim,
        n_agents=n_agents,
        steps=steps,
        noise_std=noise_std,
        seed=seed,
        phasewall_enabled=False,
        phasewall_strength=phasewall_strength,
    )
    phasewall = _simulate(
        dim=dim,
        n_agents=n_agents,
        steps=steps,
        noise_std=noise_std,
        seed=seed,
        phasewall_enabled=True,
        phasewall_strength=phasewall_strength,
    )

    return {
        "vanilla": {
            "trajectories": vanilla.trajectories,
            "metrics": {
                "escape_rate": vanilla.escape_rate,
                "inside_fraction": vanilla.inside_fraction,
                "angular_dispersion": vanilla.angular_dispersion,
                "score": vanilla.score,
            },
        },
        "phasewall": {
            "trajectories": phasewall.trajectories,
            "metrics": {
                "escape_rate": phasewall.escape_rate,
                "inside_fraction": phasewall.inside_fraction,
                "angular_dispersion": phasewall.angular_dispersion,
                "score": phasewall.score,
            },
        },
    }


def run_walker_scenario(config: ScenarioConfig) -> list[RunResult]:
    if config.engine != "walker":
        raise ValueError(f"Expected walker engine, got {config.engine}")

    out: list[RunResult] = []
    for seed in config.seeds:
        for method in ("vanilla", "phasewall"):
            trace = _simulate(
                dim=config.dim,
                n_agents=config.n_agents,
                steps=config.steps_or_evals,
                noise_std=config.noise_std,
                seed=seed,
                phasewall_enabled=method == "phasewall",
                phasewall_strength=config.phasewall_strength,
                sigma=config.sigma,
            )
            out.append(
                RunResult(
                    scenario=config.name,
                    engine=config.engine,
                    method=method,
                    seed=seed,
                    score=trace.score,
                    metrics={
                        "escape_rate": trace.escape_rate,
                        "inside_fraction": trace.inside_fraction,
                        "angular_dispersion": trace.angular_dispersion,
                    },
                )
            )

    return out
