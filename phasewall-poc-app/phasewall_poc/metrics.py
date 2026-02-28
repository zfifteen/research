from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy import stats

from .config import AggregateResult, RunResult


def bootstrap_ci(values: np.ndarray, q_low: float = 2.5, q_high: float = 97.5, n_boot: int = 2000) -> tuple[float, float]:
    if len(values) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(0)
    draws = rng.choice(values, size=(n_boot, len(values)), replace=True)
    meds = np.median(draws, axis=1)
    return float(np.percentile(meds, q_low)), float(np.percentile(meds, q_high))


def _safe_ratio(value: float, baseline: float) -> float:
    if baseline <= 0 or value < 0:
        return float("nan")
    return value / max(1e-12, baseline)


def aggregate_results(results: list[RunResult]) -> list[AggregateResult]:
    grouped: dict[tuple[str, str, str], list[RunResult]] = defaultdict(list)
    for row in results:
        grouped[(row.scenario, row.engine, row.method)].append(row)

    by_pair: dict[tuple[str, str], dict[str, list[RunResult]]] = defaultdict(dict)
    for (scenario, engine, method), rows in grouped.items():
        by_pair[(scenario, engine)][method] = rows

    out: list[AggregateResult] = []
    for (scenario, engine), method_map in sorted(by_pair.items()):
        baseline_rows = method_map.get("vanilla", [])
        baseline_scores = np.array([r.score for r in baseline_rows], dtype=float)

        baseline_by_seed = {r.seed: r.score for r in baseline_rows}

        for method, rows in sorted(method_map.items()):
            scores = np.array([r.score for r in rows], dtype=float)
            ci_low, ci_high = bootstrap_ci(scores)
            ratio = float("nan")
            p = float("nan")
            win_rate = float("nan")

            if len(baseline_scores) > 0:
                ratio = _safe_ratio(float(np.median(scores)), float(np.median(baseline_scores)))

                paired_a: list[float] = []
                paired_b: list[float] = []
                for r in rows:
                    if r.seed in baseline_by_seed:
                        paired_a.append(baseline_by_seed[r.seed])
                        paired_b.append(r.score)

                if len(paired_a) >= 2 and method != "vanilla":
                    try:
                        _, p = stats.wilcoxon(np.array(paired_a), np.array(paired_b), alternative="greater")
                    except Exception:
                        p = float("nan")
                    win_rate = float(np.mean(np.array(paired_b) < np.array(paired_a)))
                elif method == "vanilla":
                    win_rate = 0.5

            out.append(
                AggregateResult(
                    scenario=scenario,
                    engine=engine,
                    method=method,
                    n=len(scores),
                    median_score=float(np.median(scores)),
                    mean_score=float(np.mean(scores)),
                    std_score=float(np.std(scores)),
                    ci_low=ci_low,
                    ci_high=ci_high,
                    win_rate=win_rate,
                    ratio_vs_vanilla=ratio,
                    wilcoxon_p=p,
                )
            )

    return out
