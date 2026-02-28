# PhaseWall PoC App (Standalone, Local-First MVP)

## Summary
Build a new standalone app at `/Users/velocityworks/IdeaProjects/research/phasewall-poc-app` that proves the core insight from [README.md](../../README.md): the Gaussian surface has a curvature sign flip at the 1σ ring, and phase-aware update rules can improve stability/performance.

This PoC will be:
1. Interactive web app (`Streamlit + Plotly`).
2. Visual + quantitative proof.
3. Two-tier engine scope: toy dynamics plus CMA-ES-style benchmark evidence.
4. Local-first research MVP (not production SaaS).

## Scope
1. Include a geometry explainer with live 3D/2D visualizations of the 1σ phase wall.
2. Include a walker simulator showing vanilla vs phase-aware trajectories side-by-side.
3. Include an optimizer benchmark pane showing vanilla vs PhaseWall (toy ES + CMA-ES-compatible mode).
4. Include exportable evidence artifacts (CSV + PNG + markdown summary).
5. Exclude multi-user hosting, auth, backend services, and cloud infra.

## Architecture
1. **UI Layer (Streamlit)**
- `app.py` with 4 pages/tabs: Surface, Walker Arena, Optimizer Arena, Evidence Report.

2. **Core Library (`phasewall_poc/`)**
- `geometry.py`: Gaussian hill, gradients, curvature sign, ring calculations.
- `phasewall.py`: radius check, soft damping, hard projection, radial/tangential decomposition.
- `sim_walkers.py`: noisy walker/pathfinding simulation.
- `sim_optimizers.py`: toy ES and CMA-ES-compatible sampling loop.
- `metrics.py`: convergence, dispersion, ring-crossing, inside-wall occupancy, improvement ratios.
- `reporting.py`: artifact writing and markdown summary generation.
- `config.py`: typed run presets and reproducibility controls.

3. **Artifacts**
- `artifacts/<timestamp>/results.csv`
- `artifacts/<timestamp>/fig_*.png`
- `artifacts/<timestamp>/summary.md`

## Public Interfaces / Types
1. CLI entry points:
- `python -m phasewall_poc.run_demo`
- `python -m phasewall_poc.run_bench --preset core --seeds 20 --out artifacts/latest`

2. Public config types:
- `ScenarioConfig`: `name`, `dim`, `noise_std`, `steps_or_evals`, `seeds`, `phasewall_strength`, `engine`.
- `RunResult`: per-seed metrics.
- `AggregateResult`: medians, CIs, p-values, win-rate.

3. Public function contracts:
- `apply_phase_wall_z(z, r0, strength) -> z_damped`
- `compute_curvature_sign(r, sigma=1.0) -> {-1,0,+1}`
- `run_walker_scenario(config) -> list[RunResult]`
- `run_optimizer_scenario(config) -> list[RunResult]`

## Implementation Plan
1. **Scaffold repo**
- Create package structure, `pyproject.toml`, dependency lock, and base README.
- Add reproducibility defaults (global seed plumbing).

2. **Geometry + PhaseWall kernel**
- Implement normalized Gaussian surface (`sigma=1`) and curvature sign model.
- Implement soft damping and optional hard projection.
- Implement Mahalanobis-distance mode for anisotropic/high-D cases.

3. **Toy walker simulator**
- Add baseline isotropic-noise walker.
- Add phase-aware walker with radial/tangential control beyond 1σ.
- Emit per-step logs for ring-crossing and angular dispersion.

4. **Optimizer simulator**
- Add toy ES baseline + PhaseWall ES.
- Add CMA-ES-compatible run mode mirroring ask/eval/tell flow.
- Keep `x_for_eval` vs `x_for_tell` separation in PhaseWall mode.

5. **UI build**
- Surface page: 3D hill + 1σ contour + curvature map.
- Walker page: trajectory overlays + inside-wall fraction + scattering metrics.
- Optimizer page: convergence curves + seed-aggregated stats.
- Evidence page: one-click benchmark run and artifact export.

6. **Reporting**
- Generate machine-readable CSV and human-readable markdown summary.
- Include scenario config snapshot and seed list in each run output.

7. **QA + docs**
- Add unit/integration tests.
- Add “how to run” and “how to reproduce claim” sections in README.

## Test Cases and Scenarios
1. **Unit tests**
- `apply_phase_wall_z` preserves direction and clamps strength to `[0,1]`.
- Curvature sign flips at `r = sigma` (within numeric tolerance).
- Mahalanobis radius computation matches isotropic radius in identity-covariance case.

2. **Simulation tests**
- Fixed seed reproducibility for walker and optimizer outputs.
- Phase-aware mode reduces or matches ring-escape rate in default noisy walker preset.
- Phase-aware mode does not degrade deterministic/no-noise baseline behavior.

3. **Benchmark scenarios**
- Core suite: Sphere, Rosenbrock, Rastrigin in 2D/10D (toy ES), plus CMA-ES-compatible noisy tasks.
- 20-seed aggregate with median best-value comparison and Wilcoxon signed-rank p-values.
- Report win-rate and effect sizes, not only single-seed examples.

4. **Acceptance criteria**
- Visual proof: clear curvature regime split at 1σ and obvious trajectory behavior difference.
- Quant proof: exported benchmark report with reproducible seed-based comparisons.
- Usability: app boots locally with one command and exports artifacts without manual edits.

## Assumptions and Defaults
1. `sigma=1.0` normalized geometry is the canonical visual explanation.
2. Default PhaseWall strength is `0.4` with slider range `[0.0, 1.0]`.
3. Primary noise model is Gaussian additive noise.
4. First release is local-only MVP; deployment packaging is deferred.
5. Repo location is a new sibling project under `/Users/velocityworks/IdeaProjects/research`.
6. “Proof” means both intuitive visuals and reproducible statistics, not publication-grade theorem proof.
