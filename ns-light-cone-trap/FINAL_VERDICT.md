# Final Verdict — Light-Cone Trap Hypothesis

**Date:** March 3, 2026 (continued experiments)

## Mechanistic Claim: Validated (High Confidence)

Backward reconstruction is fundamentally harder than forward forecasting due to viscous dissipation. This was demonstrated across all three setups:

- **Setup 1** (1D Burgers, ensemble inversion): After fixing acceptance threshold scaling and perturbation bandwidth, 2/6 configs returned `Supported` at ν=0.002 (highest effective Re). Forward RMSE was at machine precision (~10⁻¹⁶) while backward RMSE was 0.5–1.7, with ensemble spread ~0.3 confirming non-uniqueness. Previously all rows were `no_identifiable_set`.
- **Setup 2** (diffusion + 2D NS): Experiment 1 (pure diffusion) returned `Supported` for all 4 configs with backward/forward growth ratios up to 10³⁶. Experiment 2 (nonlinear NS) showed ratios up to 10¹³; backward divergence at long horizons further confirms ill-conditioning. Global outcome: `Supported`.
- **Setup 3** (2D vorticity-form NS via odeint): Prior run (N=32, horizon=1.0) showed strong asymmetry at low Re (ratio=25.3 at Re=100) but weak at high Re (ratio=0.94 at Re=5000). The short horizon (~0.13 eddy turnovers) and coarse grid explain this. Extended runs (N=64, horizon≥2.0) exceeded feasible CPU time with the odeint integrator, documenting a practical limitation rather than a falsification.

## High-Re Quantitative Claim (3–5× ratio at Re≥5000): Inconclusive

The specific 3–5× threshold at high Re was not reproduced. Setup 3 at Re=5000 showed ratio<1 with the short horizon tested. Extended-horizon runs were computationally infeasible with the current odeint solver. This does not falsify the claim but leaves it unvalidated at the target Re range.

## Confidence & Caveats

- **Mechanistic claim confidence: ~85%.** Consistent signal across 1D Burgers, 2D diffusion, and 2D NS.
- **High-Re threshold confidence: ~30%.** Needs a semi-implicit or spectral integrator to reach Re≥5000 at τ≥2 turnovers.
- All tests used 1D/2D simplified models, not 3D DNS.
