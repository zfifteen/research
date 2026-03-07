# Permutation 5

Script: [`green_paper_permutation_5.py`](/Users/velocityworks/IdeaProjects/research/gray-scott-replication-signaling-chaos/permutation_5/green_paper_permutation_5.py)

This permutation is built to match the complete framing in:
- [`CONJECTURE.md`](/Users/velocityworks/IdeaProjects/research/gray-scott-replication-signaling-chaos/CONJECTURE.md)
- [`MORE.md`](/Users/velocityworks/IdeaProjects/research/gray-scott-replication-signaling-chaos/MORE.md)

## Features
- Measured `Pe_r = L^2/(D_u*tau_r)` from simulation-derived `L` and `tau_r`.
- Explicit `tau_r(D_u)` and `L(D_u)` visibility.
- Quench vs ramp intervention protocols using same start/end diffusivity.
- Second-ratio analysis (`t_reorg / t_intervention`) for control efficacy.

## CLI
- `--quick`
- `--seed`
- `--grid`
- `--steps`
- `--output-dir`
- `--skip-heavy`

## Outputs
- `metrics_sweep.csv`
- `metrics_protocols.csv`
- `fig1_sweep_core_metrics.png`
- `fig2_estimator_agreement.png`
- `fig3_quadratic_sensitivity.png`
- `fig4_consistency_derivative.png`
- `fig5_protocol_quench_vs_ramp_timeseries.png`
- `fig6_intervention_ratio_effect.png`
