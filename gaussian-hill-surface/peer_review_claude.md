

# Peer Re-Review: PhaseWall Technical Specification v2.1

**Verdict: Approved for Implementation**

---

## Resolution Tracker

Every item flagged in the v2.0 review has been addressed:

| v2.0 Required Item | v2.1 Resolution | Status |
|---|---|---|
| Specify implementation target (cmaes vs Optuna layer) | Section 4 defines primary path (cmaes PR) and fallback (Optuna wrapper), referencing existing `(x_for_eval, x_for_tell)` pattern | ✅ |
| Clamp strength / floor scale to prevent direction-flip | `scale = np.clip(scale, 0.0, 1.0)` in core function | ✅ |
| Fix in-place mutation; prescribe copy pattern | `z = z.copy()` at top of function; docstring states "Returns copy" | ✅ |
| Add ill-conditioned benchmark function | Ellipsoid (cond=1e6) added to benchmark matrix | ✅ |
| Define "1.5x" precisely | "median final best value at fixed evaluation budget (1,000 evals); report ratio vs vanilla + Wilcoxon p-value" | ✅ |
| Performance criteria offline, not CI-gated | "Performance improvements reported offline in PR description (not enforced in CI)" | ✅ |
| Decouple Streamlit demo | "optional community stretch goal (decoupled from core PR)" | ✅ |
| Label r₀ as approximation | "Wilson-Hilferty approximation" with accuracy table showing <0.2% error for d>=5 | ✅ |
| Document ranking/CSA interaction risk | Developer Note explicitly flags "mild selection pressure toward larger steps under noise" | ✅ |

---

## Technical Soundness Assessment

**The spec is now airtight on every point that previously had a gap.**

The code is clean, the math is correct, the integration paths are concrete, and the risks are honestly documented. Three points worth highlighting as particularly well-handled:

1. **The dual-path integration strategy is pragmatic.** Patching `cmaes` to return `(x_for_eval, x_for_tell)` is the right primary target because that library already has this exact contract for CMAwM. The Optuna fallback via `trial.system_attrs` is a sensible bridge if the cmaes PR takes longer to merge. This gives the team a shippable path regardless of upstream timelines.

2. **The r₀ verification table settles the chi vs chi-squared confusion definitively.** The v2.0 review had one model (incorrectly) claiming the formula was off by 3x, confusing the chi-squared median (~d - 2/3) with the chi median (~sqrt(d - 2/3)). The explicit table with true median values eliminates any future confusion during implementation.

3. **The acceptance criteria are now testable and non-fragile.** "Bitwise-identical sampling when strength=None" is the strongest possible regression guarantee. Reporting performance offline rather than gating CI on stochastic benchmarks is the right call for upstream maintainability.

---

## Remaining Nits (Non-Blocking)

These are suggestions for the PR description or implementation comments, not spec changes:

**N1. Noise model unspecified in benchmark description.**
The spec says "noisy Sphere, Rosenbrock, Rastrigin" but doesn't define the noise. Standard practice is additive Gaussian: `f_noisy(x) = f(x) + sigma_n * N(0, 1)`. Specify sigma_n (common choices: sigma_n = 1.0 or sigma_n proportional to f(x*)). This can go in the benchmark script docstring rather than the spec itself.

**N2. Evaluation budget may be tight for 20D noisy Rastrigin.**
With default population size (lambda ~ 13 for d=20), 1,000 evals gives ~77 generations. On noisy multi-modal landscapes this may not show convergence, only early-phase behavior. Consider either:
- Increasing to 5,000 evals for the 20D cases, or
- Reporting convergence curves (not just final values) so reviewers can see trajectory differences even if neither method fully converges.

**N3. Consider adding a deterministic regression test to the benchmark matrix.**
The acceptance criteria say "no regression on deterministic objectives" but the benchmark script only lists noisy functions plus Ellipsoid (which could be noisy or deterministic -- not specified). Adding one clean deterministic run (e.g., noise-free Sphere or Rosenbrock with PhaseWall enabled) as a sanity check would make the PR self-contained.

**N4. One-line addition for the Developer Note.**
The `cmaes` library exposes internal state via `optimizer._C`, `optimizer._mean`, `optimizer._sigma`. If the fallback path needs to compute the whitening transform externally, note that these attributes exist but are private API, and that patching cmaes directly avoids depending on them.

---

## Final Assessment

This spec has been through three review rounds and has addressed every substantive issue raised. The design is:

- **Mathematically correct** (whitened z-space, dimension-aware threshold, soft damping)
- **Computationally negligible** (O(pop_size * d) norms + scaling, no matrix operations)
- **Implementation-specified** (two concrete paths, both leveraging existing codebase patterns)
- **Numerically safe** (copy semantics, scale clamping, strength validation)
- **Honestly framed** (motivation not proof, performance to be validated, risks documented)
- **Upstream-friendly** (zero-breaking-change, optional parameter, decoupled demo)

Ship it.