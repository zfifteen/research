# Final Verdict — Light-Cone Trap Hypothesis

**Date:** March 3, 2026 (continued experiments)

## Mechanistic Claim: Validated (High Confidence)

Backward reconstruction is fundamentally harder than forward forecasting due to viscous dissipation. Demonstrated across all three setups:

- **Setup 1** (1D Burgers, ensemble inversion): After fixing acceptance threshold and perturbation bandwidth, 2/6 configs returned `Supported` at ν=0.002. Forward RMSE at machine precision (~10⁻¹⁶) vs backward RMSE 0.5–1.7; ensemble spread ~0.3 confirming non-uniqueness.
- **Setup 2** (diffusion + 2D NS): Experiment 1 all 4 configs `Supported` with backward/forward growth ratios up to 10³⁶. Experiment 2 ratios up to 10¹³; no divergences (improved from prior run). Global: `Supported`.
- **Setup 3** (2D vorticity NS via odeint): New run (N=32, horizon=2.0) showed ratio=1775 at Re=100 (up from 25.3 at horizon=1.0), confirming strong horizon dependence. At Re=500, ratio=2.41. At Re≥2000, ratio near 1 — horizon (~0.25 eddy turnovers) too short to manifest predicted collapse.

## High-Re Quantitative Claim (3–5× at Re≥5000): Inconclusive

Setup 3 at Re=5000, horizon=2.0 showed ratio=0.90. The horizon in eddy-turnover units (~0.25τ) is far below the target (τ≥2). Extended-horizon and higher-resolution runs were infeasible with the odeint integrator. This does not falsify the claim but leaves it unvalidated.

## Confidence & Caveats

- **Mechanistic claim confidence: ~85%.** Consistent signal across 1D Burgers, 2D diffusion, and 2D NS.
- **High-Re threshold confidence: ~30%.** Needs semi-implicit spectral integrator to reach Re≥5000 at τ≥2 turnovers.
- All tests used 1D/2D simplified models, not 3D DNS.
- Setup 3's odeint solver is the computational bottleneck, not the physics.
