### Technical Specification v2.0 – PhaseWall: Noise-Robust Radial Damping for Optuna’s CmaEsSampler
**Version:** 2.0 (post-peer-review)  
**Date:** 28 February 2026  
**Status:** Implementation-ready

#### 1. Objective
Add an optional, zero-breaking-change radial-damping mechanism inside `CmaEsSampler` that softly damps outliers in the whitened sampling distribution. Goal: improve robustness on noisy or multi-modal black-box objectives by 1.5–3× sample efficiency (to be validated in benchmarks) while preserving all CMA-ES adaptation invariants.

#### 2. Motivation (not proof)
In the 2D case, the graph surface of a Gaussian PDF z = exp(−r²/2) has Gaussian curvature that flips sign exactly at r = 1 (positive inside, negative outside). This inspired the intuition that “extreme samples in the proposal distribution contribute disproportionately more noise than signal under noisy fitness evaluations.” In higher dimensions we generalize conservatively via established ES practice: softly limit the radial component of whitened samples beyond the natural scale √d.

#### 3. Core Mechanism (whitened z-space)
CMA-ES internally draws z ∼ 𝒩(0, I), then x = m + σ B D z.  
We apply soft damping only on the norm of z:

```python
def apply_phase_wall_z(z: np.ndarray, r0: float, strength: float = 0.4) -> np.ndarray:
    """Soft radial damping in whitened space."""
    norms = np.linalg.norm(z, axis=1)
    outside = norms > r0
    if np.any(outside):
        scale = 1.0 - strength * (1.0 - r0 / norms[outside])
        z[outside] *= scale[:, None]
    return z
```

`r0 = np.sqrt(d - 2/3)` (median of χ(d)) — dimension-aware, parameter-free.

#### 4. Integration (ask/tell safe)
- Hook inside the underlying `cmaes.CMA` or in `CmaEsSampler._sample_relative` **before** the z → x transform (or store original z).
- Evaluate f(x_projected), but `tell()` the **original** z with the new fitness.
- Optional param: `phasewall_strength: Optional[float] = None` (None = off, default 0.4 when enabled).

#### 5. Deliverables (same as v1 but updated)
1. `PhaseWallCmaEsSampler` subclass or optional arg on `CmaEsSampler`
2. Benchmark script with:
   - 10D/20D noisy Sphere, Rosenbrock, Rastrigin
   - Baselines: vanilla, `lr_adapt=True`, 4×popsize
   - 20 seeds, wall-time + final value + statistical tests
3. Docs page + tutorial example
4. Streamlit demo (“AI Tuning Race”)
5. Full tests, ruff/mypy clean

#### 6. Acceptance Criteria
- No regression on deterministic objectives
- ≥1.5× improvement on at least two noisy functions vs vanilla (vs lr_adapt to be reported)
- All CMA-ES invariants preserved (verified by identical behavior when strength=None)
- Numerical stability to 100D

---

### Developer & Reviewer Note v2.0

**To:** Perplexity Computer engineers & Optuna reviewers

**Key changes from v1.0 (addressing all critical feedback):**
- Switched to whitened z-space + soft damping (no collapse, no Cholesky overhead, ask/tell safe).
- Dimension-aware r0 (median χ(d)).
- Explicit tell-strategy: original z + projected fitness.
- Curvature now “2D motivation” only; no d-parity claims.
- Added lr_adapt=True and popsize baselines.
- Tone moderated: “empirically improves robustness” not “free 2–4× geometric oracle”.

**Implementation priority order:**
1. Intercept at z level (cleanest).
2. Store original_z → evaluate projected_x → tell(original_z, f(projected_x)).

This version should pass upstream review cleanly. The underlying idea (limit extreme proposal steps under noise) is well-precedented in ES literature; we’re just making it one-line optional and geometrically inspired.

---
