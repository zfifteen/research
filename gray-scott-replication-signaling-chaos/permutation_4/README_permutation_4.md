# Permutation 4: Accuracy-First Validation of `CONJECTURE.md`

Script: [`green_paper_permutation_4.py`](/Users/velocityworks/IdeaProjects/research/gray-scott-replication-signaling-chaos/permutation_4/green_paper_permutation_4.py)

## Goal
This permutation prioritizes measured quantities over fitted proxies:
- `tau_r` is estimated from measured split events in Gray-Scott simulations.
- `L` is estimated from nearest-neighbor spot spacing and cross-checked with spectral wavelength.
- `Pe_r` is computed directly as `L^2 / (D_u * tau_r)` from measured values.

## CLI
- `--quick`: reduced runtime preview.
- `--seed <int>`: deterministic base seed.
- `--grid <int>`: simulation grid size.
- `--steps <int>`: simulation step count.
- `--output-dir <path>`: output directory.
- `--skip-heavy`: skip reproducibility probe.

## Outputs
Default output directory:
[`permutation_4/outputs`](/Users/velocityworks/IdeaProjects/research/gray-scott-replication-signaling-chaos/permutation_4/outputs)

Artifacts:
- `metrics.csv`: single run-level metrics table (all seeds and `D_u` values).
- `fig_claim1_estimator_agreement.png`
- `fig_claim2_transition_pe_near_one.png`
- `fig_claim3_orthogonal_control.png`
- `fig_claim4_quadratic_sensitivity.png`
- `fig_consistency_checks.png`

## Figure-to-Conjecture Mapping
Source of truth: [`CONJECTURE.md`](/Users/velocityworks/IdeaProjects/research/gray-scott-replication-signaling-chaos/CONJECTURE.md)

1. `Pe_r = L^2/(D_u*tau_r)` is the organizing variable:
   - `metrics.csv` (measured `L`, measured `tau_r`, measured `Pe_r`)
   - `fig_claim1_estimator_agreement.png` (robustness of `L` estimate)

2. Crossing `Pe_r ~ 1` tracks transition behavior:
   - `fig_claim2_transition_pe_near_one.png`

3. Raising `D_u` alone can restore order (fixed chemistry):
   - `fig_claim3_orthogonal_control.png`

4. Quadratic sensitivity in spacing (`~L^2`):
   - `fig_claim4_quadratic_sensitivity.png`

Consistency and non-artifact guardrail:
- `fig_consistency_checks.png` verifies `dPe_r/dD_u < 0` when `L` and `tau_r` are held fixed.

## Notes on Method
- Solver: explicit Euler with CFL-based auto time-step reduction.
- Spot detection: connected components on thresholded activator field.
- Split detection: spatial-neighborhood + area-gain heuristics between sampled frames.
- Uncertainty: medians with bootstrap confidence intervals.
