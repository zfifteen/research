from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .config import AggregateResult, RunResult, ScenarioConfig


def ensure_artifact_dir(base_out: Path) -> Path:
    if base_out.name == "latest":
        base_out.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        out = base_out.parent / ts
    else:
        out = base_out
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_results_csv(results: list[RunResult], path: Path) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "engine", "method", "seed", "score", "metrics"])
        for r in results:
            w.writerow([r.scenario, r.engine, r.method, r.seed, f"{r.score:.12g}", r.metrics])


def write_summary_md(
    aggregates: list[AggregateResult],
    scenarios: list[ScenarioConfig],
    seed_count: int,
    path: Path,
) -> None:
    lines: list[str] = []
    lines.append("# PhaseWall PoC Benchmark Summary")
    lines.append("")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append(f"Seeds per scenario: {seed_count}")
    lines.append("")

    lines.append("## Configuration snapshot")
    lines.append("")
    for sc in scenarios:
        lines.append(
            f"- `{sc.name}`: engine={sc.engine}, objective={sc.objective}, dim={sc.dim}, "
            f"noise={sc.noise_std}, budget={sc.steps_or_evals}, pop={sc.population_size}, "
            f"phasewall_strength={sc.phasewall_strength}"
        )
    lines.append("")

    lines.append("## Aggregated results")
    lines.append("")
    lines.append("| scenario | engine | method | n | median | ratio_vs_vanilla | win_rate | wilcoxon_p |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for a in aggregates:
        lines.append(
            "| "
            + f"{a.scenario} | {a.engine} | {a.method} | {a.n} | {a.median_score:.6g} | "
            + f"{a.ratio_vs_vanilla:.4g} | {a.win_rate:.3f} | {a.wilcoxon_p:.4g} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- Lower score is better in all scenarios.")
    lines.append("- `ratio_vs_vanilla < 1` indicates improvement.")
    lines.append("- `wilcoxon_p < 0.05` indicates paired-seed significance for `phasewall` vs `vanilla`.")

    path.write_text("\n".join(lines))


def plot_score_bars(aggregates: list[AggregateResult], path: Path) -> None:
    rows = [a for a in aggregates if a.method in {"vanilla", "phasewall"}]
    labels = sorted({(a.scenario, a.engine) for a in rows})
    x = np.arange(len(labels))
    width = 0.36

    vanilla = []
    phase = []
    for scenario, engine in labels:
        v = next(a for a in rows if a.scenario == scenario and a.engine == engine and a.method == "vanilla")
        p = next(a for a in rows if a.scenario == scenario and a.engine == engine and a.method == "phasewall")
        vanilla.append(v.median_score)
        phase.append(p.median_score)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(x - width / 2, vanilla, width, label="vanilla")
    ax.bar(x + width / 2, phase, width, label="phasewall")
    ax.set_ylabel("Median score (lower is better)")
    ax.set_title("Median performance by scenario")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s}\n({e})" for s, e in labels], rotation=45, ha="right", fontsize=8)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_win_rate(aggregates: list[AggregateResult], path: Path) -> None:
    rows = [a for a in aggregates if a.method == "phasewall"]
    rows.sort(key=lambda r: (r.engine, r.scenario))

    fig, ax = plt.subplots(figsize=(14, 4))
    x = np.arange(len(rows))
    vals = [r.win_rate for r in rows]
    ax.bar(x, vals, color="#2ecc71")
    ax.axhline(0.5, color="red", linestyle="--", linewidth=1)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Win-rate vs vanilla")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r.scenario}\n({r.engine})" for r in rows], rotation=45, ha="right", fontsize=8)
    ax.set_title("PhaseWall paired-seed win-rate")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def write_bundle(
    *,
    out_dir: Path,
    results: list[RunResult],
    aggregates: list[AggregateResult],
    scenarios: list[ScenarioConfig],
    seed_count: int,
) -> None:
    write_results_csv(results, out_dir / "results.csv")
    write_summary_md(aggregates, scenarios, seed_count, out_dir / "summary.md")
    plot_score_bars(aggregates, out_dir / "fig_score_bars.png")
    plot_win_rate(aggregates, out_dir / "fig_win_rate.png")
