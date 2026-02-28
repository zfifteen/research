from __future__ import annotations

from pathlib import Path

from phasewall_poc.run_bench import run_benchmark


def test_benchmark_writes_artifacts(tmp_path: Path) -> None:
    _, aggs, out = run_benchmark(
        preset="core",
        seed_count=2,
        out_dir=tmp_path / "latest",
    )
    assert len(aggs) > 0
    assert (out / "results.csv").exists()
    assert (out / "summary.md").exists()
    assert (out / "fig_score_bars.png").exists()
    assert (out / "fig_win_rate.png").exists()
