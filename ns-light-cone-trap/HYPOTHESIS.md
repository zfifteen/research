# Light-Cone Trap Hypothesis

The Navier–Stokes equations encode a hidden temporal irreversibility trap: viscous dissipation creates an asymmetric branching structure in the future light cone of turbulent flows that makes backward prediction fundamentally harder than forward prediction, even when the equations themselves are time-reversible under velocity sign flip.

Most treatments emphasize that Navier–Stokes with viscosity breaks time-reversal symmetry through the second-derivative viscous term, which always dissipates energy. What remains non-obvious is that this dissipation does not simply make the past harder to reach; it creates an exponentially expanding tree of plausible past states for any given present turbulent configuration, while the future collapses toward fewer statistically likely attractors.

This means that in high-Reynolds-number turbulent regimes, you can forecast aggregate statistics (energy spectra, dissipation rates, mixing timescales) with reasonable skill over multiple eddy turnover times, but retroactively diagnosing which specific initial vorticity field produced the current state becomes combinatorially explosive, because viscosity has erased the fine-scale information that would discriminate among exponentially many precursor candidates.

The testable implication is that data assimilation and state reconstruction errors should grow *faster* when running turbulent simulations backward in time than forward, even when using identical numerical schemes and error tolerances, because the backward problem is effectively inverting a many-to-one dissipative map.

This predicts that forensic fluid reconstruction tasks (determining spill sources from downstream contamination, reconstructing explosion origins from witness blast-wave data, inferring atmospheric release points from distant sensor plumes) will hit a skill ceiling much earlier in the reconstruction time horizon than equivalent forward-propagation forecasts, and that ceiling drops nonlinearly as the Reynolds number of the intervening flow increases.

The decision rule is: when Reynolds number exceeds roughly 5,000 and reconstruction time exceeds two integral eddy turnover times, switch from deterministic back-tracking to ensemble probabilistic inversion with explicit prior regularization, because deterministic backward integration will have entered the regime where solution non-uniqueness dominates truncation error.

---

## Z-Framework Quantitative Encoding

**Observable quantity (a):** Reconstruction skill score (dimensionless, 0 to 1), defined as the fraction of true initial vorticity modes above the Kolmogorov scale that are recovered within 20% amplitude error from present-state turbulent data.

**Rate quantity (b):** Information loss rate in bits per eddy turnover time, measured as the decay rate of resolvable vorticity gradients into sub-grid dissipation.

**Invariant limit (c):** Maximum information capacity of the inertial range in bits, set by the number of independent Fourier modes between the integral scale and the Kolmogorov dissipation cutoff (scales as \( \text{Re}^{9/4} \) in three-dimensional turbulence).

**Dimensionless intensity:**
\[ z = \text{(current skill)} \times \frac{\text{(loss rate)}}{\text{(capacity)}} \]

When \( z \) exceeds approximately 0.15, backward reconstruction has entered the regime where dissipation-induced solution branching overwhelms measurement precision, and deterministic inversion becomes structurally infeasible regardless of algorithm refinement.

## Falsification Criteria

**This insight is falsified if:**

High-Reynolds-number turbulent flow reconstruction experiments (Re > 10,000, reconstruction horizon > 3 eddy turnovers) consistently achieve backward-integrated state errors that remain within the same order of magnitude as forward-integrated errors when both use identical numerical methods and assimilation data density.

**This insight is supported if:**

Controlled experiments using DNS or laboratory particle-image velocimetry show that backward reconstruction error grows at least 3–5× faster than forward forecast error over equivalent time intervals once Reynolds number exceeds 5,000, even when the same adjoint or ensemble Kalman methods are applied symmetrically in both directions.