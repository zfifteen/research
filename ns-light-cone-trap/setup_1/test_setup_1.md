# test_setup_1.md
## Test Setup 1 — No-Lab Validation in Python (1D Viscous Burgers)

### Goal
Test the core claim of the **Light-Cone Trap Hypothesis** in a fully controlled simulation:

- Forward prediction of coarse flow properties can remain usable over a horizon τ,
- while **backward reconstruction of the past from the present becomes ill-conditioned** (non-unique / prior-dominated) beyond a smaller horizon τ\* under realistic observation noise.

This setup is designed to be:
- runnable on a laptop,
- reproducible (fixed seeds),
- interpretable (clean mechanism: viscosity destroys fine-scale information).

---

## Model and domain

### PDE
1D viscous Burgers equation on a periodic domain:

	t u_t + u u_x = ν u_xx

- ν > 0 is the viscosity (controls dissipation).
- Burgers is the minimal “turbulence-bearing” dissipative PDE where backward inversion becomes unstable in a controlled way.

### Domain
- x ∈ [0, 2π), periodic
- Discretize with N grid points (spectral FFT)

Suggested defaults:
- N = 1024 (works well on most laptops)
- ν ∈ {1e-2, 5e-3, 2e-3, 1e-3} (sweep)

---

## “Truth” simulation

### Initial condition
Choose a smooth, multi-mode field so that nonlinear steepening generates small scales:

Example:
- sum of random-phase Fourier modes with a low-wavenumber envelope (k ≤ k0)

Fix a random seed.

### Time integration
- pseudo-spectral method:
  - compute u_x in Fourier space
  - nonlinear term in physical space
  - viscosity in Fourier space
- stable integrator:
  - ETDRK4 (best), or
  - RK4 with sufficiently small dt and viscosity handled explicitly

Record the full state u(x,t) at all times needed.

### Time horizon and “turnover time”
Define a characteristic turnover time:
- T_eddy = L / U_rms   (L = 2π)

Use it to express horizons in “eddy turnovers”:
- τ = Δt / T_eddy

---

## Observation model at final time

### Define observation operator H
You need an information bottleneck so that the inverse is non-unique under noise.

Pick one of these:

**H1: low-pass Fourier observation**
- observe only modes |k| ≤ k_obs
- add Gaussian noise in observed mode amplitudes

**H2: downsampled spatial observation**
- observe u at M << N equally spaced points
- add Gaussian noise to samples

Recommended:
- H1 with k_obs ≈ N/16 or N/32
- This mimics “finite-resolution sensors.”

### Noise level
- ε = noise standard deviation
- run a sweep over ε (e.g., 1e-4, 1e-3, 1e-2 relative to U_rms)

Observed data:
- y = H(u(T)) + η,  η ~ N(0, ε^2 I)

---

## Two tasks to compare (core of the test)

Let τ be the reconstruction horizon.

### Task A — Forward forecast (baseline)
Given the true past state u(T−τ), forecast forward to T:

- û_fwd(T) = F^τ(u(T−τ))

Measure:
- RMSE_fwd(τ) = ||û_fwd(T) − u(T)|| / ||u(T)||

This is “how hard it is to go forward.”

### Task B — Backward reconstruction (inverse)
Given only y at time T, reconstruct the past state u(T−τ).

This is the inverse problem:
- find candidate past states ũ(T−τ) such that H(F^τ(ũ(T−τ))) matches y within ε.

You cannot “integrate backward” stably with ν>0, so you do *inference*.

---

## Reconstruction method (laptop-feasible)

### Ensemble inversion (recommended)
Generate K candidate past states by optimizing with different initial guesses:

1. Initialize K candidates:
   - ũ_i(T−τ) = u(T−τ) + small random perturbations (or a smoothed prior)
2. For each candidate, run forward:
   - y_i = H(F^τ(ũ_i(T−τ)))
3. Accept / refine candidates that satisfy:
   - ||y_i − y|| ≤ c·ε   (c ~ 2–3)

Optional refinement:
- gradient-free optimization (Nelder–Mead) or simple iterative updates
- or a light EnKF-style correction in the reduced observation space

Key point:
- you are not trying to find “the” past.
- you are measuring how the *set* of plausible pasts grows with τ.

---

## Metrics (what to plot and what “branching” means)

### 1) Backward reconstruction error (best fit)
Take the best-fitting candidate and compare to truth:

- RMSE_bwd(τ) = min_i ||ũ_i(T−τ) − u(T−τ)|| / ||u(T−τ)||

### 2) Branching proxy (non-uniqueness)
Compute spread across all accepted candidates:

- Spread(τ) = mean_x Var_i[ũ_i(T−τ, x)]^{1/2}

Or in Fourier space:
- Spread_k(τ) = mean_k Var_i[û̃_i(T−τ, k)]^{1/2}

This is the operational “tree width.”

### 3) Prior-dominance proxy (optional)
If you impose regularization (e.g., smoothing prior), track:
- how strong the regularization must be to keep RMSE_bwd bounded.

---

## Pass / fail criteria for this setup

### Supported (in this computational setting) if:
- there exists a τ* such that, for τ > τ*:
  - RMSE_bwd(τ) grows much faster than RMSE_fwd(τ), and/or
  - Spread(τ) increases rapidly (many plausible pasts fit the same y),
  - while forward error remains comparatively modest for coarse metrics.

### Falsified (in this computational setting) if:
- backward reconstruction remains comparable to forward forecasting over τ ≥ 2–3 turnover units
  **without** rapidly increasing Spread(τ) and **without** stronger priors.

Note: this is not a claim about all flows. It is a controlled test of the mechanism your hypothesis asserts.

---

## Suggested parameter sweep (minimal but informative)
- ν ∈ {1e-2, 5e-3, 2e-3, 1e-3}
- k_obs ∈ {N/16, N/32}
- ε_rel ∈ {1e-4, 1e-3, 1e-2}
- τ ∈ [0.25, 3.0] turnover units (e.g., 12–20 points)

Expected qualitative trend:
- smaller ν (higher “effective Re”) → smaller τ* and faster spread growth.

---

## Outputs checklist
Your script should produce:

- Plot 1: RMSE_fwd(τ) vs τ
- Plot 2: RMSE_bwd(τ) vs τ
- Plot 3: Spread(τ) vs τ  (branching proxy)
- Terminal summary:
  - estimated τ*
  - slopes / ratios (e.g., backward growth vs forward growth)
  - pass/fail against stated criteria

---

## Notes / limitations (be explicit)
- This setup is 1D and not full 3D Navier–Stokes.
- It tests the **information-destroying inversion mechanism** (dissipation + finite observation), which is the critical engine of your hypothesis.
- If it passes here, it motivates scaling up to 2D vorticity or 3D DNS when resources exist.

