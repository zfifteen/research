# Light-Cone Trap Hypothesis

Turbulent backward reconstruction is fundamentally harder than forward forecasting, not because the equations contain a “hidden branching,” but because viscosity makes the *inverse problem ill-conditioned*: dissipation erases the small-scale information that distinguishes many different past microstates that map to the same present macrostate.

Most treatments note that Navier–Stokes with viscosity breaks time-reversal symmetry through the viscous term and energy dissipation. The non-obvious part is operational: at high Reynolds number, the forward dynamics can retain *predictive skill for coarse observables* (spectra, dissipation statistics, mixing timescales) over multiple eddy turnover times, while the backward task becomes a many-to-one inversion under noise. In other words, the “tree” is not a literal dynamical branching in the PDE; it is the growth of the *set of compatible past states* under finite observation error and finite resolution.

Testable implication: with matched observation models, numerical tolerances, and assimilation budgets, **backward smoothing / reconstruction skill should collapse at a shorter horizon (in turnover units) than forward forecasting skill**, because backward inference is forced to invert a dissipative map whose conditioning deteriorates rapidly once the discriminating fine scales have been advected into the dissipation range.

Practical implication: forensic fluid reconstruction (source finding from downstream plumes, blast/impact origin inference from sparse field data, atmospheric release reconstruction) will hit a skill ceiling earlier than comparable forward propagation predictions. That ceiling should fall nonlinearly as Reynolds number increases, because the inertial range expands and more degrees of freedom must be inferred while the observations remain finite.

Decision rule (non-arbitrary form): switch from deterministic backtracking to **ensemble probabilistic inversion with explicit priors/regularization** when diagnostics show that reconstruction uncertainty (ensemble spread or adjoint sensitivity norm) grows superlinearly with reconstruction horizon τ (in eddy turnovers). A rough starting point for calibration is that this often appears once Re is O(10^3–10^4) and τ exceeds O(1–3), but the trigger should be the *measured conditioning*, not a hard-coded Re threshold.

---

## Z-Framework Quantitative Encoding

**Observable quantity (a):** Reconstruction skill score (dimensionless, 0 to 1), defined as the fraction of true initial vorticity modes above the Kolmogorov scale recovered within 20% amplitude error from present-state data.

**Rate quantity (b):** Information loss rate in bits per eddy turnover time, measured as the decay rate of resolvable vorticity-gradient information into sub-grid dissipation.

**Invariant limit (c):** Maximum information capacity of the inertial range in bits, set by the number of dynamically relevant Fourier modes between the integral scale and the Kolmogorov cutoff (under Kolmogorov scaling assumptions, this grows like Re^{9/4} in 3D turbulence).

**Dimensionless intensity over a reconstruction horizon τ (in eddy turnovers):**
\[
z(\tau) = (1-\text{skill}) \times \frac{\text{(loss rate)}\cdot \tau}{\text{(capacity)}}
\]

Interpretation:
- (1 − skill) ensures z increases as reconstruction degrades.
- Multiplying by τ makes z dimensionless (since (b) is a rate).
- z(\tau) is an operational “ill-conditioning intensity” for how far back you are trying to infer.

When z(τ) exceeds a calibrated threshold z*, backward reconstruction is dominated by non-uniqueness/conditioning rather than truncation error, and deterministic inversion becomes structurally unreliable without a strong prior.

---

## Falsification Criteria

**Falsified if:**
In controlled high-Re experiments (e.g., Re > 10,000) with matched observation operators and noise ε, backward smoothing/reconstruction maintains comparable error growth to forward prediction over τ ≥ 3 eddy turnovers *without* requiring materially stronger priors/regularization in the backward direction.

**Supported if:**
DNS or laboratory PIV-based experiments show that, beyond a measured conditioning crossover (captured by rapid growth in ensemble spread or adjoint sensitivity), backward reconstruction error (or required posterior entropy) grows at least ~3–5× faster than forward forecast error over the same τ, under symmetric assimilation methods and comparable information budgets.