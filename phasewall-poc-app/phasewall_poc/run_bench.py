from __future__ import annotations

import argparse
from pathlib import Path

from .config import core_benchmark_scenarios
from .metrics import aggregate_results
from .reporting import ensure_artifact_dir, write_bundle
from .sim_optimizers import run_optimizer_scenario
from .sim_walkers import run_walker_scenario


def run_benchmark(preset: str, seed_count: int, out_dir: Path) -> tuple[list, list, Path]:
    if preset != "core":
        raise ValueError(f"Unsupported preset: {preset}")

    scenarios = core_benchmark_scenarios(seed_count=seed_count)
    all_results = []
    for scenario in scenarios:
        if scenario.engine == "walker":
            all_results.extend(run_walker_scenario(scenario))
        else:
            all_results.extend(run_optimizer_scenario(scenario))

    aggs = aggregate_results(all_results)
    resolved_out = ensure_artifact_dir(out_dir)
    write_bundle(
        out_dir=resolved_out,
        results=all_results,
        aggregates=aggs,
        scenarios=scenarios,
        seed_count=seed_count,
    )

    return all_results, aggs, resolved_out


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PhaseWall PoC benchmark runner")
    parser.add_argument("--preset", default="core", choices=["core"])
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--out", type=Path, default=Path("artifacts/latest"))
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    _, aggs, out_dir = run_benchmark(
        preset=args.preset,
        seed_count=args.seeds,
        out_dir=args.out,
    )

    print(f"Artifacts written to: {out_dir}")
    for row in aggs:
        print(
            f"{row.scenario:28s} {row.engine:11s} {row.method:10s} "
            f"median={row.median_score:10.5g} ratio={row.ratio_vs_vanilla:7.4f} p={row.wilcoxon_p:8.4g}"
        )


if __name__ == "__main__":
    main()
