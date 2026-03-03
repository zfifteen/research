# Experiment Setup Document

**Validation Protocol for the z-Phase-Transition Framework**  
**Gradient Reconstruction Scheme Selection on Unstructured Polyhedral Grids**

**Version:** 1.0  
**Date:** March 3, 2026  
**Author:** Big D' (in collaboration with Grok)  

---

### Purpose

This document provides a complete, reproducible experimental protocol to rigorously validate (or falsify) the core claims of the technical note:

1. Gradient schemes exhibit a **sharp phase transition** (not smooth degradation) in performance as a function of the dimensionless metric **z**.
2. The **z-based classifier** acts as a reliable pre-filter that predicts viable scheme families from mesh geometry alone, reducing testing effort by 70–90 %.
3. Hybrid schemes (e.g., Shima–Kitamura–Haga GLSQ) deliver 5–20× advantage **only** inside the narrow transition band (3 < z < 6 in the note’s scaling).

The protocol is designed for a single researcher or small team to execute in 1–2 weeks on a standard workstation (no HPC required for the manufactured-solution phase).

### 1. Required Software & Environment

- **Mesh generator:** Pointwise, ANSYS Fluent meshing, or Gmsh + custom Python script (preferred for automation).
- **CFD solver framework:** OpenFOAM (v2312+), SU2, or a minimal standalone FVM library in Python/C++ (for manufactured-solution tests only).
- **Post-processing:** ParaView 5.12+, Python 3.11+ (numpy, scipy, matplotlib, vtk).
- **Version control:** Git commit after each major step.
- **Reproducibility:** Docker image or conda environment `cfd-z-validation` with pinned versions.

### 2. Mesh Generation Suite (Controlled Skewness)

Generate a family of **2D unstructured triangular/polygonal meshes** first (faster iteration), then extend to 3D polyhedral.

**Base domain:** Unit cube [0,1]³ or 2D square [0,1]².

**Skewness control parameter:** Target maximum non-orthogonality angle θ_skew ∈ {10°, 30°, 50°, 60°, 70°, 80°}.

**Procedure (Python + Gmsh or Pointwise script):**
1. Create base isotropic mesh (≈ 10 k cells 2D / 100 k cells 3D).
2. Apply controlled distortion:
    - Random node perturbation scaled to achieve desired max θ_skew.
    - Or use explicit transformation: stretch cells in one direction while preserving connectivity.
    - For polyhedral: convert tets → poly via OpenFOAM `polyDualMesh` or Gmsh `polyhedral` option.
3. Export 6 meshes (one per θ_skew value) + one “production-like” mixed mesh (blend 20 % low-z, 15 % transition, 65 % high-z cells).
4. For each mesh compute and store:
    - z-field using the exact formula in `technical_note_2.md` Section 3.1.
    - Histogram and color-coded ParaView .vtk output (blue = low-z, orange = transition, green = high-z).

**Expected z-ranges (p=2):**
- θ_skew=10° → z≈17.0 (high)
- θ_skew=30° → z≈5.7 (high/edge of transition)
- θ_skew=50° → z≈3.4 (transition)
- θ_skew=60° → z≈2.8 (transition)
- θ_skew=70° → z≈2.4 (low/edge)
- θ_skew=80° → z≈2.1 (low)

**Deliverable:** Folder `meshes/` containing 7 .vtk/.foam files + `z_fields/` with .csv summary tables.

### 3. Gradient Reconstruction Schemes to Implement

**Minimal set (exactly 3 core schemes – no more!):**
1. **Pure Green-Gauss (volume-weighted)** – reference robust first-order.
2. **Pure Weighted Least-Squares (inverse-distance or geometric weighting)** – reference high-order.
3. **Shima–Kitamura–Haga GLSQ hybrid** (β blending based on local aspect ratio or z) with tunable α ∈ {0.0, 0.5, 1.0}.

**Implementation notes:**
- Use the exact 2013 AIAA J. 51(11) formulation for GLSQ.
- In OpenFOAM: extend `fvMesh` with a new `zAwareGrad` class that reads pre-computed z-field and selects per-cell.
- In Python standalone: vectorized NumPy implementation for manufactured-solution tests (no full solver needed).
- Record CPU time per gradient evaluation (10⁶ evaluations).

### 4. Manufactured-Solution Test Procedure (Primary Hypothesis Test)

**Field:**  
f(x,y,z) = sin(πx) cos(πy) exp(z/L) with L=1.0 (analytic gradient known exactly).

**Steps for each mesh + each scheme:**
1. Store cell-centered values of f.
2. Reconstruct ∇f at cell centers using the three schemes.
3. Compute L² error:
   ```math
   E = \sqrt{ \frac{1}{N} \sum_i |∇f_{recon,i} - ∇f_{exact,i}|^2 \cdot V_i }
   ```
4. Also record:
    - Max monotonicity violation |C|max (should be <1 for robust schemes).
    - CPU time.
5. Repeat for 5 different random seeds on mesh distortion to get statistics (mean ± std).

**Total runs:** 6 meshes × 3 schemes × 3 α values × 5 seeds = 270 evaluations (≈ 2–3 hours on laptop).

**Analysis script:** `analyze_phase_transition.py` that:
- Plots error vs. θ_skew (or vs. mean z).
- Overlays predicted table from technical note Section 4.1.
- Computes “hybrid advantage ratio” = max(pure error) / hybrid error.
- Generates the exact color-coded z-map + regime statistics.

### 5. Production-Mesh Economic Test (Pre-Filter Validation)

**Mesh:** Real external aerodynamics case (e.g., 2D airfoil or 3D DrivAer vehicle, ~1–5 M cells, mixed quality).

**Workflow A (Traditional – baseline):**
- Implement all 8–10 candidate schemes.
- Run full gradient reconstruction + simple steady laminar flow solve.
- Record final drag coefficient error vs. reference, total wall time, memory.

**Workflow B (z-Filtered):**
1. Run geometry scan → z-report (30 s).
2. Follow Case A/B/C/D decision tree exactly as written in technical note Section 3.3.
3. Implement only the 2–4 recommended schemes.
4. Run same flow solve.

**Metrics to compare:**
- Final solution accuracy (drag/lift error).
- Total developer time logged (use `git commit` timestamps + manual log).
- Number of test runs executed.
- Lines of code added/maintained.

**Success criterion:** Workflow B ≥ 95 % of Workflow A accuracy with ≤ 30 % of the effort.

### 6. Data Collection & Reporting Template

Create folder `results/YYYY-MM-DD_run/` containing:
- `z_histogram.png`, `error_vs_z.png`, `hybrid_advantage.png`
- `summary_table.csv` (exact columns from technical note Table in 4.1 + measured values)
- `regime_report.md` (auto-generated by the Python function in note Section 5.1)
- `falsification_log.md` (any deviations from predictions)

### 7. Timeline & Milestones (1-Week Execution)

**Day 1:** Mesh suite generation + z-field verification.  
**Day 2:** Implement 3 core gradient schemes (Python standalone).  
**Day 3:** Run manufactured-solution matrix.  
**Day 4:** Generate plots + compare to predicted table.  
**Day 5:** Production-mesh test (Workflow A vs. B).  
**Day 6:** Write results section + falsification assessment.  
**Day 7:** Commit everything, update `technical_note_2.md` with real numbers, tag release `v1.0-experiment-results`.

### 8. Falsification Criteria (Explicit)

- **Hypothesis fails** if: hybrid advantage is flat or smoothly varying across z (no sharp 5–20× peak inside 3 < z < 6).
- **Filter fails** if: z-classification leads to >5 % worse final solution accuracy or >50 % more effort than traditional approach.
- **z-formula fails** if: different skewness definitions (e.g., ANSYS vs. OpenFOAM) produce inconsistent regime predictions.

### 9. Next Steps After Validation

If successful:
- Publish short note + this experiment setup as companion arXiv preprint.
- Release open-source `zAwareGrad` module for OpenFOAM/SU2.
- Extend to full NS solver + viscous flux tests.

If any falsification triggers: refine z formula (add aspect-ratio or condition-number term) and re-run.

---