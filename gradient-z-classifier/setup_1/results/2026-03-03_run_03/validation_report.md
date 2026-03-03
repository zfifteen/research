# Validation Report

- Run directory: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03`
- Hypothesis status: **FALSIFIED**

## Controlled Skewness Family

| θ_skew target | z-range (mean) | Pure LSQ error | Pure GG error | GLSQ (α=0.5) error | Hybrid advantage |
|---|---|---:|---:|---:|---:|
| 50° | 1.98-340.00 (13.97) | 2.672e-01 | 3.780e+00 | 1.898e+00 | 1.991x |

## Regime Statistics per Mesh

| Mesh | Mean z | High-z (%) | Transition (%) | Low-z (%) |
|---|---:|---:|---:|---:|
| skew_50deg | 13.97 | 52.5 | 40.5 | 7.0 |

## Falsification Assessment

- Phase-transition hypothesis falsified because peak hybrid advantage is 1.99x at mean z=13.97, which does not satisfy the z∈[3,6] and advantage≥5 criterion.

## Output File Paths

- Raw long metrics: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/raw/metrics_long.csv`
- Summary table: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/raw/summary_by_mesh.csv`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/plots/error_vs_theta.png`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/plots/hybrid_advantage_vs_z.png`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/plots/representative_mesh_z_and_error.png`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_03/plots/regime_histogram_summary.png`
