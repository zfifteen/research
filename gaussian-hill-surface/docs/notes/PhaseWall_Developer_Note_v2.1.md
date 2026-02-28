# Developer & Reviewer Note v2.1

**To:** Perplexity Computer engineers, Optuna & cmaes maintainers

**Summary**  
All peer-review feedback incorporated. This is a clean, minimal, optional feature.

**Key implementation notes**
- Primary: patch `cmaes` using existing `(x_for_eval, x_for_tell)` pattern.
- Fallback: Optuna wrapper via `trial.system_attrs["x_for_tell"] = list(original_x.flatten())` (serialization-safe).
- `apply_phase_wall_z` returns a copy — caller can safely pass original z.
- Strength clamped [0.0, 1.0] inside function.
- r₀ is lightweight approximation (error <0.2% for d≥5).
- Damping applied to internal z **before** x mapping and any feasibility/bounds repair.

**Risks (explicit)**  
Mild selection pressure toward larger steps under noise (outlier z’s get evaluated closer to mean). Monitor in benchmarks.

This version is ready for coding and should review cleanly upstream.
