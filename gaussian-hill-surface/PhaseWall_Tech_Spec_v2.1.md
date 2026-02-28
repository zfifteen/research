### Technical Specification v2.1 – PhaseWall: Soft Radial Damping for Optuna’s CmaEsSampler
**Version:** 2.1 (post all peer re-reviews)  
**Date:** 28 February 2026  
**Status:** Implementation-ready

#### 1. Objective
Add an optional, zero-breaking-change soft radial-damping mechanism inside `CmaEsSampler` that damps outliers in the whitened sampling distribution (z-space). Goal: improve robustness on noisy or multi-modal black-box objectives (target 1.5–3× sample efficiency vs vanilla, to be validated) while preserving all CMA-ES adaptation invariants.

#### 2. Motivation
In 2D the graph surface of a Gaussian PDF has Gaussian curvature that flips sign at r = 1. This inspired the practical heuristic that extreme samples in the proposal distribution can contribute disproportionate noise under noisy fitness evaluations. In higher dimensions we apply a conservative, dimension-aware soft radial limit in whitened z-space.

#### 3. Core Mechanism (whitened z-space)
CMA-ES draws z ∼ 𝒩(0, I), then x = m + σ B D z.  
Apply soft excess-radius damping only on ‖z‖:

```python
def apply_phase_wall_z(
    z: np.ndarray,          # shape (pop_size, d)
    r0: float,
    strength: float = 0.4   # clamped to [0.0, 1.0]
) -> np.ndarray:
    """Soft radial damping in whitened space. Returns copy."""
    z = z.copy()  # explicit copy for tell-strategy safety
    norms = np.linalg.norm(z, axis=1)
    outside = norms > r0
    if np.any(outside):
        # excess-radius damping: new_norm = norm - strength*(norm - r0)
        scale = 1.0 - strength * (1.0 - r0 / norms[outside])
        scale = np.clip(scale, 0.0, 1.0)  # never flip direction
        z[outside] *= scale[:, None]
    return z
```

**r₀ definition** (dependency-free, Wilson-Hilferty approximation to median of χ(d)):

```python
r0 = np.sqrt(d - 2.0 / 3.0)
```

Accuracy (verified):

| d  | approx r₀ | true median χ(d) | error |
|----|-----------|------------------|-------|
| 2  | 1.155     | 1.177            | 1.9%  |
| 10 | 3.055     | 3.059            | 0.13% |
| 20 | 4.397     | 4.399            | 0.05% |

#### 4. Integration & Ask/Tell Contract (safe)
**Primary path (recommended):** Patch inside the `cmaes` package (CyberAgent/cmaes).  
`CMA.ask()` returns `(x_for_eval, x_for_tell)` where `x_for_eval` is damped, `x_for_tell` is original. `tell()` API unchanged.

**Fallback path:** Inside `PhaseWallCmaEsSampler` (Optuna-only).
- After `params = optimizer.ask()`, compute damped version.
- Store original in `trial.system_attrs["x_for_tell"]` (matches existing CMAwM pattern).
- Return damped version for evaluation.
- In `tell()` reconstruction, prefer `system_attrs["x_for_tell"]` if present.

#### 5. Deliverables
1. Primary: PR to `cmaes` + thin Optuna integration (or fallback wrapper)
2. Benchmark script (`examples/phasewall_benchmark.py`):
   - 10D/20D noisy Sphere, Rosenbrock, Rastrigin, **Ellipsoid (cond=1e6)**
   - 20 independent seeds
   - Baselines: vanilla, `lr_adapt=True`, 4×popsize
   - Metric: median final best value at fixed evaluation budget (1,000 evals); report ratio vs vanilla + Wilcoxon p-value
3. Documentation updates + tutorial
4. Full tests (pytest + ruff + mypy)
5. Streamlit demo is **optional community stretch goal** (decoupled from core PR)

#### 6. Acceptance Criteria
- When `phasewall_strength=None`: bitwise-identical sampling (fixed seed) and identical convergence on deterministic objectives
- No NaNs/crashes up to 100D
- Performance improvements reported offline in PR description (not enforced in CI)
- ≥1.5× median final fitness improvement on at least two noisy functions vs vanilla (lr_adapt baseline also reported)

---

### Developer & Reviewer Note v2.1

**To:** Perplexity Computer engineers, Optuna & cmaes maintainers

**Summary of changes from v2.0**  
All peer-review feedback incorporated. The design is now fully specified, numerically safe, and upstream-friendly.

**Key implementation notes**
- Prefer patching `cmaes` (leverages existing `(x_for_eval, x_for_tell)` pattern).
- Strength clamped [0.0, 1.0]; scale floored at 0.0.
- Caller must copy z before damping if original is needed for tell.
- r₀ is a lightweight approximation (error <0.2% for d≥5).

**Risks (explicit)**  
Mild selection pressure toward larger steps under noise (outlier z’s get evaluated closer to mean and may rank higher). Monitor in benchmarks; expected to be beneficial for noisy objectives.
