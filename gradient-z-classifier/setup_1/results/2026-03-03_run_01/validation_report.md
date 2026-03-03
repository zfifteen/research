# Validation Report

- Run directory: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01`
- Hypothesis status: **FALSIFIED**

## Controlled Skewness Family

| θ_skew target | z-range (mean) | Pure LSQ error | Pure GG error | GLSQ (α=0.5) error | Hybrid advantage |
|---|---|---:|---:|---:|---:|
| 10° | 1.89-170.35 (6.31) | 4.314e-02 | 8.835e-01 | 4.420e-01 | 1.999x |
| 30° | 1.93-340.00 (7.66) | 3.893e-01 | 2.154e+00 | 1.114e+00 | 1.933x |
| 50° | 1.98-340.00 (13.97) | 2.672e-01 | 3.780e+00 | 1.898e+00 | 1.991x |
| 60° | 1.93-340.00 (15.59) | 2.933e-01 | 3.576e+00 | 1.800e+00 | 1.987x |
| 70° | 1.98-340.00 (17.32) | 3.410e-01 | 3.555e+00 | 1.794e+00 | 1.982x |
| 80° | 1.90-340.00 (15.13) | 4.626e-01 | 5.234e+00 | 2.636e+00 | 1.985x |

## Regime Statistics per Mesh

| Mesh | Mean z | High-z (%) | Transition (%) | Low-z (%) |
|---|---:|---:|---:|---:|
| skew_10deg | 6.31 | 38.7 | 59.9 | 1.4 |
| skew_30deg | 7.66 | 43.1 | 50.9 | 6.0 |
| skew_50deg | 13.97 | 52.5 | 40.5 | 7.0 |
| skew_60deg | 15.59 | 52.9 | 36.4 | 10.6 |
| skew_70deg | 17.32 | 56.4 | 37.8 | 5.9 |
| skew_80deg | 15.13 | 54.2 | 38.7 | 7.1 |

## Falsification Assessment

- Phase-transition hypothesis falsified because peak hybrid advantage is 2.00x at mean z=6.31, which does not satisfy the z∈[3,6] and advantage≥5 criterion.

## Mixed Production Mesh (Economic Test Preview)

| Mesh | z-range (mean) | GG error | WLSQ error | GLSQ (α=0.5) error | High-z (%) | Transition (%) | Low-z (%) |
|---|---|---:|---:|---:|---:|---:|---:|
| mixed_production | 1.89-26.45 (2.15) | 1.666e+00 | 1.050e-01 | 8.359e-01 | 0.1 | 2.1 | 97.8 |

## Output File Paths

- Raw long metrics: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/raw/metrics_long.csv`
- Summary table: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/raw/summary_by_mesh.csv`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/plots/error_vs_theta.png`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/plots/hybrid_advantage_vs_z.png`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/plots/representative_mesh_z_and_error.png`
- Plot: `/Users/velocityworks/IdeaProjects/research/gradient-z-classifier/setup_1/results/2026-03-03_run_01/plots/regime_histogram_summary.png`
