The common boundary used to measure normal spread is not just a statistical milestone, but a strict spatial phase wall where a system's fundamental shape entirely collapses and reverses.

We typically view bell-shaped distributions as uniformly smooth fades that slowly taper away from a central peak.

However, analyzing the physical surface of this curve reveals it is actually constructed from two fundamentally opposed environments joined perfectly at this specific ring.

Inside this boundary zone, the landscape acts like a converging bowl that naturally gathers moving elements together.

The moment you cross this specific perimeter, the landscape instantly flattens before aggressively warping into a repelling saddle that forces elements apart.

This suggests we should stop treating these distributions as continuous, predictable slopes and instead view them as stable cores surrounded by inherently unstable outer fields.

We would not have predicted that systems governed by these curves possess a built-in geometric trap exactly at their designated spread limit.

If you deploy a pathfinding algorithm to climb a perfectly normal gradient, you should expect to measure an abrupt, severe spike in directional scattering the exact moment the path crosses this hidden perimeter.
---
## The Thesis
The 1σ boundary is not merely descriptive statistics. It is an algorithmic control surface.

When a Gaussian is viewed as geometry rather than just probability mass, `r = σ` marks a regime boundary:

- `r < σ`: elliptic, convergence-friendly interior
- `r = σ`: zero-curvature transition
- `r > σ`: hyperbolic, scattering-prone exterior

That turns a textbook contour into an operational decision rule for stochastic systems.

## Two Claims
### 1) Geometry Claim
For the isotropic Gaussian hill `z = exp(-r^2 / (2σ^2))`, Gaussian curvature changes sign exactly at `r = σ`.

Equivalently, after simplification:

`K(r) ∝ (σ^2 - r^2) / positive_term`

The sign switch is exact, not heuristic.

### 2) Algorithm Claim
If update dynamics are made phase-aware at this boundary, instability can be reduced in noisy search, sampling, and control loops that use Gaussian assumptions.

This is not a claim that every objective improves. It is a claim that many stochastic pipelines can become more stable and sample-efficient when they respect this geometric transition.

![Gaussian Hill and Curvature Regimes](artifacts/figures/concepts/img.png)

## The Control Rule
For any method with a center and spread estimate:

1. Estimate center `μ` and local spread (scalar `σ` or covariance `Σ`).
2. Compute normalized radius:
   - isotropic: `r = ||x - μ|| / σ`
   - anisotropic: `r = sqrt((x - μ)^T Σ^-1 (x - μ))` (Mahalanobis radius)
3. Switch behavior by phase:
   - inside wall (`r <= 1`): standard dynamics
   - outside wall (`r > 1`): damp tangential noise/steps, bias inward radial component

In high dimensions, the same idea is applied in whitened proposal space (`z ~ N(0, I)`), where only excess radius is softly damped.

```python
def apply_phase_wall_z(z, r0, strength=0.4):
    z = z.copy()
    norms = np.linalg.norm(z, axis=1)
    outside = norms > r0
    if np.any(outside):
        scale = 1.0 - strength * (1.0 - r0 / norms[outside])
        scale = np.clip(scale, 0.0, 1.0)
        z[outside] *= scale[:, None]
    return z
```

Practical default for dimension `d`:

`r0 ≈ sqrt(d - 2/3)`

This approximates the median radius of `χ(d)` and keeps the rule dimension-aware with negligible overhead.

## Why This Has Broad Impact
Any software stack that uses Gaussian proposals, Gaussian noise models, or local quadratic approximations is exposed to this regime transition.

Representative targets:

- Evolutionary strategies (`ES`, `CMA-ES`, `NES`)
- Particle methods (`PSO`, SMC/particle filters)
- Noisy gradient methods (`SGD` variants, Langevin/SGLD)
- MCMC proposals and importance samplers
- Bayesian optimization and trust-region loops
- Gaussian policy exploration in RL
- Risk engines and simulation workflows that rely on Gaussian state evolution

The key idea is simple: stop treating all Gaussian radii as equivalent terrain.

## Evidence Snapshot
### Walker Dynamics on Exact Gaussian Surface
Internal runs with `1500+` noisy walkers on `z = exp(-r^2/2)`:

- baseline (isotropic noise, no phase rule):
  success `31.7%`, avg steps `32.9`, mean final radius `0.570`
- phase-aware switching at `r = 1`:
  success `32.8%`, avg steps `30.2` (~8% faster), mean final radius `0.551`

Under stronger noise stress, measured gains rose to:

- `1.5x-2.2x` higher success
- `40%-52%` fewer steps
- `25%-35%` tighter final clustering

![Walker End-State Comparison](artifacts/figures/concepts/img_1.png)

### Optimizer Benchmarks
From current benchmark artifacts:

- Sphere: `2.42x` improvement
- Rosenbrock: `3.88x` improvement
- Rastrigin: `1.47x` improvement
- Additional stress runs showed up to `4.2x` on noisy 20D Sphere

Related plots and report are in this repository:

- `artifacts/figures/benchmarks/benchmark_bars.png`
- `artifacts/figures/benchmarks/benchmark_ratios.png`
- `docs/analysis/benchmarks.md`
- `artifacts/reports/PhaseWall_Benchmark_Report.pdf`

## Reproducibility Standard
The recommended evaluation protocol is paired-seed and budget-fixed:

- compare phase-aware vs vanilla under identical seeds
- report median final score at fixed evaluation budget
- include paired statistical test (for example Wilcoxon)
- include deterministic/no-noise regression check to verify no degradation

This keeps results honest and prevents storytelling from outrunning evidence.

## Boundary Conditions and Risks
This approach is high leverage, but not magic.

- It helps most when noise/outliers dominate update quality.
- On clean deterministic problems, gains may be neutral.
- Poor center/covariance estimates can misplace the wall.
- Damping may introduce mild ranking bias in population methods if not monitored.
- Use soft damping first; hard projection should be opt-in.

The right framing is a geometry-guided stabilizer, not a universal optimizer replacement.

## Falsifiable Predictions
This thesis should be rejected if repeated experiments show:

- no systematic reduction in escape/scattering outside the wall
- no sample-efficiency improvement on noisy benchmark families
- consistent degradation on deterministic baselines when enabled conservatively
- no statistical separation from baseline under paired-seed evaluation

If those outcomes occur, the rule is not broadly useful and should remain a niche geometric observation.

## Repository Guide
- `docs/specs/PhaseWall_Tech_Spec_v2.1.md`: implementation-level mechanism and acceptance criteria
- `docs/notes/PhaseWall_Developer_Note_v2.1.md`: reviewer-facing integration notes
- `docs/notes/PhaseWall_Sandbox_Playbook_v2.1.md`: execution flow for constrained environments
- `docs/analysis/benchmarks.md` and `artifacts/reports/PhaseWall_Benchmark_Report.pdf`: quantitative results
- `docs/analysis/practical_application.md`: deployment-oriented integration sketches
- `docs/reviews/peer_review_*.md`: critique history and design hardening

## References
[1] Closed-form Gaussian hill curvature sign structure and the `r = σ` transition (see local technical spec and benchmark notes).

[2] Standard differential-geometry point classification by Gaussian curvature sign (elliptic/parabolic/hyperbolic), applied here to Gaussian graph surfaces.
