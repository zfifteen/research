from __future__ import annotations

from pathlib import Path

from .run_bench import run_benchmark


def main() -> None:
    print("Running PhaseWall PoC quick demo benchmark (core preset, 6 seeds)...")
    _, aggs, out_dir = run_benchmark(
        preset="core",
        seed_count=6,
        out_dir=Path("artifacts/latest"),
    )

    print(f"Demo artifacts: {out_dir}")
    print("Summary (phasewall rows):")
    for row in aggs:
        if row.method == "phasewall":
            print(
                f"- {row.scenario} [{row.engine}] median={row.median_score:.5g}, "
                f"ratio={row.ratio_vs_vanilla:.4f}, win_rate={row.win_rate:.3f}, p={row.wilcoxon_p:.4g}"
            )

    print("To launch UI: streamlit run app.py")


if __name__ == "__main__":
    main()
