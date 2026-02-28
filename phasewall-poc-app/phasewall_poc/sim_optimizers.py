from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import RunResult, ScenarioConfig
from .phasewall import apply_phase_wall_z


@dataclass
class OptimizerRun:
    best_history: np.ndarray
    best_final: float
    eval_count: int


OBJECTIVE_MAP = {
    "sphere": lambda x: float(np.sum(x**2)),
    "rosenbrock": lambda x: float(
        np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1.0 - x[:-1]) ** 2)
    ),
    "rastrigin": lambda x: float(10.0 * len(x) + np.sum(x**2 - 10.0 * np.cos(2.0 * np.pi * x))),
}


def _evaluate_batch(
    x_eval: np.ndarray,
    objective: str,
    noise_std: float,
    rng: np.random.Generator,
) -> np.ndarray:
    fn = OBJECTIVE_MAP[objective]
    safe_x = np.clip(x_eval, -50.0, 50.0)
    vals = np.array([fn(x) for x in safe_x], dtype=float)
    if noise_std > 0:
        vals += rng.normal(0.0, noise_std, size=len(vals))
    return vals


def _run_toy_es(
    *,
    objective: str,
    dim: int,
    eval_budget: int,
    population_size: int,
    noise_std: float,
    seed: int,
    phasewall_enabled: bool,
    phasewall_strength: float,
) -> OptimizerRun:
    rng = np.random.default_rng(seed)
    mean = np.ones(dim, dtype=float) * 3.0
    sigma = 2.0

    best = float("inf")
    history: list[float] = []
    evals = 0
    r0 = float(np.sqrt(dim - 2.0 / 3.0))

    while evals < eval_budget:
        z = rng.normal(size=(population_size, dim))
        x_tell = mean + sigma * z

        if phasewall_enabled:
            z_eval = apply_phase_wall_z(z, r0=r0, strength=phasewall_strength)
            x_eval = mean + sigma * z_eval
        else:
            x_eval = x_tell

        y = _evaluate_batch(x_eval, objective, noise_std, rng)
        best = min(best, float(np.min(y)))

        order = np.argsort(y)
        mu = population_size // 2
        elite = x_tell[order[:mu]]
        mean = np.mean(elite, axis=0)

        spread = np.mean(np.linalg.norm(elite - mean, axis=1)) / np.sqrt(dim)
        sigma = 0.85 * sigma + 0.15 * max(1e-3, spread)

        evals += population_size
        history.append(best)

    return OptimizerRun(best_history=np.array(history), best_final=best, eval_count=evals)


class CmaesStyleOptimizer:
    """Lightweight ask/eval/tell optimizer with CMA-ES-style flow."""

    def __init__(
        self,
        *,
        dim: int,
        population_size: int,
        seed: int,
        phasewall_strength: float | None,
    ) -> None:
        self.dim = dim
        self.population_size = population_size
        self._rng = np.random.default_rng(seed)
        self.mean = np.ones(dim) * 3.0
        self.sigma = 2.0
        self.diag_var = np.ones(dim, dtype=float)
        self.phasewall_strength = phasewall_strength
        self.r0 = float(np.sqrt(dim - 2.0 / 3.0))

    def ask(self) -> tuple[np.ndarray, np.ndarray] | np.ndarray:
        L = np.diag(np.sqrt(np.clip(self.diag_var, 1e-8, 1e6)))
        z = self._rng.normal(size=self.dim)
        x_tell = self.mean + self.sigma * (L @ z)

        if self.phasewall_strength is None:
            return x_tell

        z_eval = apply_phase_wall_z(z, r0=self.r0, strength=self.phasewall_strength)
        x_eval = self.mean + self.sigma * (L @ z_eval)
        return x_eval, x_tell

    def tell(self, solutions: list[tuple[np.ndarray, float]]) -> None:
        solutions.sort(key=lambda s: s[1])
        mu = self.population_size // 2
        elite = np.array([s[0] for s in solutions[:mu]], dtype=float)

        new_mean = np.mean(elite, axis=0)
        var_est = np.var(elite, axis=0)

        self.mean = np.clip(0.8 * self.mean + 0.2 * new_mean, -1e3, 1e3)
        self.diag_var = 0.9 * self.diag_var + 0.1 * np.clip(var_est, 1e-8, 1e6)

        trace = float(np.mean(self.diag_var))
        self.sigma = max(1e-3, min(10.0, 0.9 * self.sigma + 0.1 * np.sqrt(trace)))


def _run_cmaes_style(
    *,
    objective: str,
    dim: int,
    eval_budget: int,
    population_size: int,
    noise_std: float,
    seed: int,
    phasewall_enabled: bool,
    phasewall_strength: float,
) -> OptimizerRun:
    phasewall_on = phasewall_enabled and noise_std > 0.0
    opt = CmaesStyleOptimizer(
        dim=dim,
        population_size=population_size,
        seed=seed,
        phasewall_strength=phasewall_strength if phasewall_on else None,
    )
    rng = np.random.default_rng(seed + 100_000)

    best = float("inf")
    history: list[float] = []
    evals = 0

    while evals < eval_budget:
        solutions: list[tuple[np.ndarray, float]] = []
        for _ in range(opt.population_size):
            asked = opt.ask()
            if isinstance(asked, tuple):
                x_eval, x_tell = asked
            else:
                x_eval = x_tell = asked

            y = _evaluate_batch(x_eval[np.newaxis, :], objective, noise_std, rng)[0]
            best = min(best, float(y))
            solutions.append((x_tell, float(y)))
            evals += 1
            if evals >= eval_budget:
                break

        if len(solutions) == opt.population_size:
            opt.tell(solutions)

        history.append(best)

    return OptimizerRun(best_history=np.array(history), best_final=best, eval_count=evals)


def run_optimizer_scenario(config: ScenarioConfig) -> list[RunResult]:
    if config.engine not in ("toy_es", "cmaes_style"):
        raise ValueError(f"Unsupported optimizer engine: {config.engine}")

    out: list[RunResult] = []
    for seed in config.seeds:
        for method in ("vanilla", "phasewall"):
            phase = method == "phasewall"
            phase = phase and config.noise_std > 0.0
            if config.engine == "toy_es":
                run = _run_toy_es(
                    objective=config.objective,
                    dim=config.dim,
                    eval_budget=config.steps_or_evals,
                    population_size=config.population_size,
                    noise_std=config.noise_std,
                    seed=seed,
                    phasewall_enabled=phase,
                    phasewall_strength=config.phasewall_strength,
                )
            else:
                run = _run_cmaes_style(
                    objective=config.objective,
                    dim=config.dim,
                    eval_budget=config.steps_or_evals,
                    population_size=config.population_size,
                    noise_std=config.noise_std,
                    seed=seed,
                    phasewall_enabled=phase,
                    phasewall_strength=config.phasewall_strength,
                )

            out.append(
                RunResult(
                    scenario=config.name,
                    engine=config.engine,
                    method=method,
                    seed=seed,
                    score=run.best_final,
                    metrics={
                        "evals": float(run.eval_count),
                        "history_len": float(len(run.best_history)),
                    },
                )
            )

    return out


def run_optimizer_pair_demo(
    *,
    engine: str,
    objective: str,
    dim: int,
    eval_budget: int,
    population_size: int,
    noise_std: float,
    n_seeds: int,
    phasewall_strength: float,
) -> dict[str, dict[str, float | list[float]]]:
    seeds = list(range(10_000, 10_000 + n_seeds))

    vanilla_runs: list[OptimizerRun] = []
    phase_runs: list[OptimizerRun] = []
    for seed in seeds:
        if engine == "toy_es":
            vanilla_runs.append(
                _run_toy_es(
                    objective=objective,
                    dim=dim,
                    eval_budget=eval_budget,
                    population_size=population_size,
                    noise_std=noise_std,
                    seed=seed,
                    phasewall_enabled=False,
                    phasewall_strength=phasewall_strength,
                )
            )
            phase_runs.append(
                _run_toy_es(
                    objective=objective,
                    dim=dim,
                    eval_budget=eval_budget,
                    population_size=population_size,
                    noise_std=noise_std,
                    seed=seed,
                    phasewall_enabled=noise_std > 0.0,
                    phasewall_strength=phasewall_strength,
                )
            )
        elif engine == "cmaes_style":
            vanilla_runs.append(
                _run_cmaes_style(
                    objective=objective,
                    dim=dim,
                    eval_budget=eval_budget,
                    population_size=population_size,
                    noise_std=noise_std,
                    seed=seed,
                    phasewall_enabled=False,
                    phasewall_strength=phasewall_strength,
                )
            )
            phase_runs.append(
                _run_cmaes_style(
                    objective=objective,
                    dim=dim,
                    eval_budget=eval_budget,
                    population_size=population_size,
                    noise_std=noise_std,
                    seed=seed,
                    phasewall_enabled=noise_std > 0.0,
                    phasewall_strength=phasewall_strength,
                )
            )
        else:
            raise ValueError(f"Unsupported engine: {engine}")

    vanilla_final = np.array([r.best_final for r in vanilla_runs], dtype=float)
    phase_final = np.array([r.best_final for r in phase_runs], dtype=float)

    history_len = int(min(min(len(r.best_history) for r in vanilla_runs), min(len(r.best_history) for r in phase_runs)))
    vanilla_hist = np.median(np.vstack([r.best_history[:history_len] for r in vanilla_runs]), axis=0)
    phase_hist = np.median(np.vstack([r.best_history[:history_len] for r in phase_runs]), axis=0)

    x_axis = np.linspace(1, eval_budget, history_len).tolist()

    ratio = float(np.median(phase_final) / max(1e-12, np.median(vanilla_final)))
    win_rate = float(np.mean(phase_final < vanilla_final))

    return {
        "vanilla": {
            "median_final": float(np.median(vanilla_final)),
            "median_history_x": x_axis,
            "median_history_y": vanilla_hist.tolist(),
        },
        "phasewall": {
            "median_final": float(np.median(phase_final)),
            "median_history_x": x_axis,
            "median_history_y": phase_hist.tolist(),
        },
        "median_ratio": ratio,
        "win_rate": win_rate,
    }
