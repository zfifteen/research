**TASK: Implement the full manufactured-solution gradient reconstruction test harness (`test_gradients.py`)**

**Project Context**  
We are building `gradient-z-classifier` — a geometry-driven classification framework for gradient reconstruction schemes on unstructured grids (see `technical_note_2.md` in the repo root). The core hypothesis is a sharp **phase transition** controlled by the dimensionless metric  
`z = (85.0 / θ_skew) × 2`  
with three regimes:
- High-z (> 6): simple WLSQ sufficient
- Transition (3–6): hybrid GLSQ (Shima–Kitamura–Haga) shows 5–20× advantage
- Low-z (< 3): only Green-Gauss viable, or remesh

We have already generated the validation mesh family in `gradient-z-classifier/setup_1/meshes_v3/` (run `generate_meshes_v3.py` if not already done). Each folder contains:
- `mesh.vtk`
- `points.npy`, `tri.npy`, `z.npy`, `theta_skew.npy`
- `plots/z_theta.png`

**Your Task**  
Create a **complete, self-contained, ready-to-run** script `gradient-z-classifier/setup_1/test_gradients.py` that:

1. Loads every mesh in `meshes_v3/` (the 6 controlled-skewness + the mixed one)
2. Implements **exactly three core gradient reconstruction schemes** (no more):
    - Pure Green-Gauss (volume-weighted)
    - Pure Weighted Least-Squares (inverse-distance weighting)
    - Shima–Kitamura–Haga GLSQ hybrid with tunable blending parameter α ∈ {0.0, 0.5, 1.0}
3. Runs the **manufactured solution test** exactly as described in `technical_note_2.md` Section 4.1:
    - Analytic field: `f(x,y) = sin(πx) * cos(πy)` (2D is fine for speed; extend to 3D if you want bonus points)
    - Compute exact analytic gradient
    - Reconstruct gradient at cell centers using each scheme
    - Compute L² error (volume-weighted)
    - Compute max monotonicity violation (|C|_max)
    - Record CPU time per reconstruction (1e6 evaluations or full field)
4. Produces **exactly** the comparison table from the technical note (extend it with measured values):
   ```markdown
   | θ_skew target | z-range (mean) | Pure LSQ error | Pure GG error | GLSQ (α=0.5) error | Hybrid advantage |
   ```
5. Generates publication-ready plots (save to `results/YYYY-MM-DD_run/plots/`):
    - Error vs. target θ_skew (log scale, with three curves)
    - Hybrid advantage ratio (max pure / GLSQ) vs. z
    - One representative z-colored mesh with overlaid gradient error field
    - Regime histogram summary
6. Outputs a Markdown report `results/YYYY-MM-DD_run/validation_report.md` that includes:
    - The filled comparison table
    - Regime statistics per mesh
    - Clear statement: “Phase-transition hypothesis confirmed / falsified because …”
    - All file paths to plots and raw data

**Technical Requirements**
- Use only `numpy`, `scipy`, `matplotlib`, `vtk` (or pure numpy VTK reader if you prefer)
- Vectorized NumPy implementation for speed (no loops over cells where possible)
- Reproducible: `np.random.seed(42)` where needed
- Clean, well-commented code with functions:
    - `load_mesh(folder)`
    - `green_gauss_grad(...)`
    - `wlsq_grad(...)`
    - `glsq_hybrid_grad(...)` (implement the exact 2013 AIAA blending)
    - `manufactured_solution_test(mesh_folder, scheme, alpha=0.5)`
    - `run_full_validation()`
- Automatic folder creation for results (use current date)
- Run time goal: < 2 minutes on a laptop for all 7 meshes × 3 schemes × 3 alphas

**Success Criteria**
- Script runs with `python test_gradients.py` and produces the exact table format from the technical note
- Hybrid advantage shows clear peak (5–20×) in the 3 < z < 6 band
- All plots are saved and look professional
- Report contains falsification assessment text ready to paste into the technical note

**Bonus (optional but nice)**
- Support for 3D extension (just change the field to include z)
- ParaView-ready .vtu files with reconstructed gradients and error fields
- Command-line flags: `--mesh-dir`, `--output-dir`, `--schemes gg,wlsq,glsq`

**Deliverables**
- `gradient-z-classifier/setup_1/test_gradients.py`
- `results/YYYY-MM-DD_run/` folder with everything
- Update `experiment_setup.md` with “Day 3 completed” note if you want

Start by creating the file and implementing the three gradient functions first, then the full pipeline. Ping me with any questions or partial output.

---
. 🚀