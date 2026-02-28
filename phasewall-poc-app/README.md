# PhaseWall PoC App

Standalone local-first proof-of-concept for the Gaussian 1σ curvature phase-wall insight.

The app demonstrates two claims:
1. Geometry claim: the Gaussian surface curvature sign flips at radius `r = σ`.
2. Algorithm claim: phase-aware controls beyond `1σ` can reduce instability and improve search behavior.

## What is included

- Streamlit app with 4 tabs:
  - Surface (3D hill + curvature sign map + 1σ ring)
  - Walker Arena (vanilla vs phase-aware trajectories)
  - Optimizer Arena (toy ES + CMA-ES-style ask/eval/tell)
  - Evidence Report (run benchmark + export artifacts)
- Core library in `phasewall_poc/`.
- CLI entry points:
  - `python -m phasewall_poc.run_demo`
  - `python -m phasewall_poc.run_bench --preset core --seeds 20 --out artifacts/latest`
- Tests in `tests/`.

## Quick start

```bash
cd /Users/velocityworks/IdeaProjects/research/phasewall-poc-app
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
streamlit run app.py
```

## CLI usage

Run a quick local sanity demo:

```bash
python -m phasewall_poc.run_demo
```

Run the benchmark suite and export artifacts:

```bash
python -m phasewall_poc.run_bench --preset core --seeds 20 --out artifacts/latest
```

Output artifacts:

- `artifacts/<timestamp>/results.csv`
- `artifacts/<timestamp>/summary.md`
- `artifacts/<timestamp>/fig_score_bars.png`
- `artifacts/<timestamp>/fig_win_rate.png`

## Reproducing the core claim

1. Open `streamlit run app.py`.
2. In **Surface**, verify curvature sign transitions at `r=1σ`.
3. In **Walker Arena**, compare vanilla and phase-aware escape/scattering metrics.
4. In **Optimizer Arena**, compare score trajectories for vanilla vs phase-aware.
5. In **Evidence Report**, run `core` benchmark for 20 seeds and inspect exported summary.

## Notes

- This is a research MVP, not a production service.
- Default geometry normalization uses `σ=1.0`.
- Default phase-wall strength is `0.4`.
