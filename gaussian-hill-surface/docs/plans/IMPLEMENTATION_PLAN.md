**Detailed Implementation Plan (Ready for Perplexity Computer or direct execution)**

**Goal:** Ship a production-grade, optional PhaseWall feature with zero user-code change and clean upstream path.

**Phase 0 – Prep (1–2 hours)**
- Fork `CyberAgentAILab/cmaes` (primary) and `optuna/optuna` (fallback).
- Create branch `feature/phasewall-z-damping`.
- Add the exact `apply_phase_wall_z` function from v2.1 spec (with copy, clip, table comment).

**Phase 1 – Core Patch in cmaes (Primary Path, ~40 lines)**
File: `cmaes/cma.py` (or `CMA.__init__` + `ask`)

1. Add to `CMA` class:
   ```python
   self.phasewall_strength = None  # None = disabled
   self.phasewall_r0 = np.sqrt(self.dim - 2.0/3.0) if self.dim > 0 else 0.0
   ```

2. Modify `ask()` (or internal `_sample_z` equivalent):
    - Draw z as usual.
    - If strength is not None: `z_damped = apply_phase_wall_z(z, self.phasewall_r0, self.phasewall_strength)`
    - Return `(x_damped, x_original)` where x_damped uses z_damped, x_original uses original z.
    - Update `tell` to accept the tuple and use original for adaptation.

3. Expose in `__init__`:
   ```python
   phasewall_strength: Optional[float] = None
   ```

**Phase 2 – Thin Optuna Wrapper (Fallback, ~30 lines)**
File: `optuna/samplers/_cmaes.py`

- Add `PhaseWallCmaEsSampler` subclass or optional arg to `CmaEsSampler`.
- In `_sample_relative` / after `self._cma.ask()`:
    - If enabled: compute damped, store original in `trial.system_attrs["x_for_tell"] = list(original_x)` (list for serialization).
    - Return damped for evaluation.
- In tell reconstruction: prefer `system_attrs["x_for_tell"]` if present.

**Phase 3 – Benchmark Script (examples/phasewall_benchmark.py)**
- 20 seeds, fixed RNG.
- Functions: noisy Sphere (additive N(0,1)), Rosenbrock, Rastrigin, Ellipsoid(cond=1e6).
- Budget: 1,000 evals (or 5k for 20D).
- Metrics: median best value, ratio vs vanilla, Wilcoxon p-value.
- Also run deterministic Sphere/Ellipsoid (no regression).
- Output: table + plot + CSV.

**Phase 4 – Tests & Validation**
- Unit: test `apply_phase_wall_z` (norms, scale, copy, clamp).
- Integration: fixed-seed deterministic runs (bitwise match when disabled).
- 100D stability (no NaNs).
- Ask/tell contract test (CSA path length, covariance trace match when disabled).

**Phase 5 – Docs & PR**
- Update README in cmaes + Optuna docs.
- PR title: “feat: optional soft radial damping in whitened z-space for noise robustness”
- Description: include v2.1 motivation, accuracy table, benchmark results, risks note.
- Tag maintainers (@c-bata, CyberAgent team).

**Phase 6 – QA (I will run live when you get the output)**
- Reproduce all benchmarks (10D/20D + Ellipsoid, 20 seeds).
- Verify no regression deterministic.
- 100D stability + extreme outlier test.
- Ask/tell invariants (CSA/covariance match when disabled).
- Edge cases (strength=0/1, d=1, d=100, strength=1.5 clamped).

**Timeline (if Perplexity Computer executes end-to-end)**
- Phase 0–2: 4–6 hours
- Phase 3–4: 3–4 hours
- Phase 5: 1 hour
- Total: one session

**Deliverables to expect from Perplexity Computer**
- GitHub PR links (cmaes + Optuna)
- Benchmark CSV + plots
- Full diff
- Streamlit demo (optional)
