# Experimental Validation Protocol

## Testing the Phase-Transition Hypothesis for Gradient Reconstruction Scheme Selection

*Big D'*  
*March 3, 2026*

**Document Purpose:** Provide complete experimental protocol to validate or falsify the z-threshold framework for gradient reconstruction on unstructured grids.

---

## Executive Summary

This protocol tests whether:
1. A dimensionless mesh quality metric z = (θ_crit / θ_skew) × p predicts discrete regime boundaries
2. Hybrid gradient schemes show 5-20× advantage specifically in 3 < z < 6 band
3. The selection filter reduces implementation effort by 70-90% without sacrificing accuracy

**Timeline:** 4-6 weeks for complete validation  
**Resources:** Single workstation, open-source CFD tools, automated test harness  
**Deliverables:** Pass/fail on 5 core predictions, calibrated z-thresholds, validated selection filter

---

## Table of Contents

1. Experiment Overview
2. Test Case Design
3. Mesh Generation Protocol
4. Gradient Scheme Implementations
5. Measurement Procedures
6. Success Criteria
7. Data Collection and Analysis
8. Experiment Execution Timeline
9. Automation and AI Integration
10. Contingency Plans
11. Appendices

---

## 1. Experiment Overview

### 1.1 Primary Hypotheses

**H1: Phase Transition Existence**  
Hybrid scheme advantage over pure methods is non-monotonic with mesh quality, showing a sharp peak in the 3 < z < 6 band rather than smooth variation.

**H2: Regime Classification Predictive Power**  
Pre-computed z-field from geometry alone predicts which scheme class will succeed, enabling >70% reduction in test matrix without accuracy loss.

**H3: Threshold Universality**  
The z-thresholds (z = 3, z = 6) apply across multiple flow types and boundary conditions, not just the specific test cases.

**H4: Economic Validation**  
Filtered workflow (Cases A/B/C/D) achieves 95%+ of exhaustive search accuracy with 60-80% less implementation effort.

**H5: Low-z Collapse**  
All second-order schemes produce errors >50% of signal magnitude when z < 3, regardless of sophistication.

### 1.2 Experimental Architecture

```
Phase 1: Controlled Synthetic Tests (2 weeks)
  └─ Isolate z as independent variable
  └─ Establish baseline regime boundaries
  └─ Calibrate thresholds

Phase 2: Production Mesh Validation (1-2 weeks)
  └─ Test on realistic CFD meshes
  └─ Verify regime classification accuracy
  └─ Measure economic benefit

Phase 3: Generalization Tests (1 week)
  └─ Multiple flow physics
  └─ Boundary condition sensitivity
  └─ Extension to 2D vs 3D

Phase 4: Filter Workflow Comparison (1 week)
  └─ Head-to-head: filtered vs exhaustive
  └─ Measure effort reduction
  └─ Validate AI assistant integration
```

### 1.3 Null Hypothesis (Disconfirmation Criteria)

The framework is **falsified** if any of the following occur:
1. Hybrid advantage varies monotonically with skewness (no peak in transition band)
2. z-field classification leads to scheme selection that underperforms exhaustive search by >5%
3. Optimal z-thresholds shift by >50% between test cases (not universal)
4. Low-z regions show some second-order schemes working well (z < 3 is not a hard limit)

---

## 2. Test Case Design

### 2.1 Primary Test Function (Analytic Gradients)

**Smooth scalar field:**

f(x, y, z) = sin(2πx/L) × cos(2πy/L) × exp(z/H)

**Known exact gradient:**

∇f = [(2π/L)cos(2πx/L)cos(2πy/L)exp(z/H),
      -(2π/L)sin(2πx/L)sin(2πy/L)exp(z/H),
      (1/H)sin(2πx/L)cos(2πy/L)exp(z/H)]

**Domain:** 
- 3D: [0, L]³ with L = 1.0 m, H = 1.0 m
- 2D: [0, L]² (z-component ignored)

**Why this function:**
- Non-trivial spatial variation in all directions
- Bounded derivatives (no singularities)
- Analytic gradient for exact error computation
- Sufficient complexity to stress reconstruction schemes

### 2.2 Secondary Test Function (Steep Gradients)

**Boundary layer profile:**

f(x, y, z) = tanh(10z) × sin(πx) × cos(πy)

**Purpose:** Test schemes under high gradient magnitude, representative of viscous flows

### 2.3 Tertiary Test Function (Multi-Scale)

**Composition:**

f(x, y, z) = sin(2πx) + 0.1sin(20πx) + 0.01sin(200πx)

**Purpose:** Evaluate high-frequency gradient capture (relevant for turbulence, shocks)

### 2.4 Flow Physics Tests (Production Validation)

**Case A: Laminar flow over flat plate**
- Reynolds number: Re = 1000
- Mesh: structured boundary layer transitioning to unstructured
- z-profile: expected high-z in freestream, transition-z in boundary layer edge

**Case B: Flow around cylinder**
- Re = 100 (steady)
- Mesh: unstructured triangular/tetrahedral with refinement near surface
- z-profile: expected low-z in wake, transition-z near stagnation

**Case C: Turbulent channel flow**
- Re_τ = 180
- Mesh: wall-resolved LES grid
- z-profile: expected transition-z throughout (challenging case)

---

## 3. Mesh Generation Protocol

### 3.1 Controlled Skewness Sequence (Phase 1)

**Objective:** Generate meshes with precise, uniform skewness levels to isolate z as independent variable.

**Methodology:**

**Base mesh:** Regular Cartesian grid
- Cells: 20 × 20 × 20 (8,000 cells)
- Domain: [0, 1]³

**Skewing transformation:**  
Apply shear to introduce controlled non-orthogonality:

x' = x  
y' = y + α × x  
z' = z

where α = tan(θ_target) controls target skewness angle.

**Skewness levels (θ_skew):** 5°, 10°, 20°, 30°, 40°, 50°, 55°, 60°, 65°, 70°, 75°, 80°, 85°

**Corresponding z-values (for p=2):** 34, 17, 8.5, 5.7, 4.25, 3.4, 3.1, 2.8, 2.6, 2.4, 2.3, 2.1, 2.0

**Mesh quality verification:**
- Compute actual θ_skew for each cell
- Verify σ(θ_skew) < 2° (uniform skewness)
- Check aspect ratio remains O(1) (isolate skewness effect)

**Output:** 13 meshes covering full z-range with dense sampling in transition band (2.5 < z < 4)

### 3.2 Aspect Ratio Variation (Decoupling Test)

**Objective:** Verify z-metric applies to stretched meshes, not just skewed ones.

**Base mesh:** Cartesian with controlled stretching
- Cells: 20 × 20 × 40
- Stretching ratio: r ∈ {1, 2, 5, 10, 20, 50}
- Orthogonality: maintained (θ_skew < 5°)

**Modified z-metric for stretching:**

z_stretch = (r_crit / r_max) × p

where r_crit ≈ 1000 (typical breakdown threshold)

**Prediction:** High aspect ratio alone (without skewness) should NOT trigger regime transition; z based on orthogonality is dominant.

### 3.3 Production Mesh Generation

**Flat plate mesh:**
- Tool: Gmsh or ICEM CFD
- Boundary layer: 20 layers, first cell height y+ < 1, growth ratio 1.2
- Transition to unstructured: tetrahedral with sizing function
- Target: f_high = 0.7, f_trans = 0.25, f_low = 0.05

**Cylinder mesh:**
- O-grid near surface (structured)
- Unstructured triangular/tetrahedral in wake
- Refinement: 3 levels, 2:1 ratio
- Target: f_trans = 0.4 (challenging transition-dominated case)

**Channel mesh:**
- Wall-resolved LES requirements: Δy+ < 1, Δx+ < 100, Δz+ < 30
- Mixed hex/prism elements
- Target: f_trans = 0.6, f_low = 0.15 (stress test)

### 3.4 Mesh Storage and Documentation

**Format:** CGNS or Gmsh .msh (portable, well-documented)

**Metadata for each mesh:**
- Skewness histogram (full distribution)
- Aspect ratio histogram
- z-field statistics (mean, std, percentiles)
- Regime fractions (f_high, f_trans, f_low)
- Cell count, face count, neighbor connectivity stats

**Repository structure:**
```
meshes/
├── controlled_skewness/
│   ├── skew_05deg.cgns
│   ├── skew_10deg.cgns
│   └── ... (13 meshes)
├── aspect_ratio/
│   ├── ar_001.cgns
│   └── ... (6 meshes)
├── production/
│   ├── flat_plate.cgns
│   ├── cylinder.cgns
│   └── channel.cgns
└── metadata/
    └── mesh_quality_report.csv
```

---

## 4. Gradient Scheme Implementations

### 4.1 Required Schemes

Implement the following to span pure → hybrid spectrum:

**Pure Methods (Baselines):**

1. **Unweighted Least-Squares (LSQ)**
   - Stencil: all face neighbors
   - Weight: uniform (w_j = 1)
   - Matrix: 3×3 (over-determined for typical stencils)

2. **Green-Gauss Cell-Based (GG)**
   - Face value: arithmetic average of neighbors
   - Integration: Σ_faces (φ_f × S_f)
   - First-order accurate in general

3. **Green-Gauss Node-Based (GG-Node)**
   - Face value: interpolated from nodes
   - Requires vertex values (auxiliary reconstruction)
   - Second-order on structured, irregular on skewed

**Weighted Methods:**

4. **Weighted Least-Squares (WLSQ)**
   - Inverse-distance weighting: w_j = 1/|r_ij|²
   - Alternative: w_j = 1/|r_ij|
   - Improves conditioning on irregular stencils

**Hybrid Methods (Key Test Candidates):**

5. **Green-Gauss/LSQ Hybrid (GLSQ)**
   - Blending: ∇φ = α(∇φ_GG) + (1-α)(∇φ_LSQ)
   - Parameter: α ∈ [0, 1]
   - Test values: α = 0.2, 0.5, 0.8

6. **Flexible Gradient (Nishikawa-style)**
   - Implicit formulation with tunable damping
   - Parameter: β controls iterative convergence
   - More expensive but highly robust

**Optional (if resources allow):**

7. **Modified Green-Gauss (MGG)**
8. **Implicit Green-Gauss (IGG)**

### 4.2 Implementation Requirements

**Language:** C++ or Fortran (performance), Python wrapper for automation

**Data structures:**
```cpp
struct Cell {
    int id;
    Vector3D center;
    double volume;
    vector<int> neighbor_ids;
    vector<Vector3D> face_centers;
    vector<Vector3D> face_areas;  // vector (magnitude + direction)
};

class GradientScheme {
    virtual Vector3D compute_gradient(int cell_id, 
                                      const vector<double>& field) = 0;
    virtual string get_name() = 0;
    virtual map<string, double> get_parameters() = 0;
};
```

**Code verification:**
- Test each scheme on uniform Cartesian grid (should all give exact gradients for linear field)
- Verify symmetry: rotating domain should not change gradient magnitude
- Conservation check: volume-weighted sum of gradients = boundary integral

**Performance tracking:**
- CPU time per gradient evaluation
- Memory footprint
- Linear solver iterations (for implicit methods)

### 4.3 Reference Implementation Strategy

**Option A: Build from scratch**
- Full control, clean code
- Effort: ~1 week for 6 schemes
- Use Eigen library for linear algebra

**Option B: Extend existing tool**
- OpenFOAM: already has fvSchemes framework
- SU2: gradient reconstruction module exists
- Effort: ~3 days to add missing schemes

**Option C: Hybrid approach**
- Write standalone gradient library (mesh-agnostic)
- Interface to multiple CFD tools via mesh adapters
- Most flexible for automation

**Recommendation:** Option C with Python bindings for experiment automation.

---

## 5. Measurement Procedures

### 5.1 Error Metrics

**Primary metric: L2 gradient error**

E_L2 = sqrt[ (1/N_cells) × Σ_i ||∇φ_computed,i - ∇φ_exact,i||² ]

**Secondary metrics:**

**L∞ error (maximum error):**
E_Linf = max_i ||∇φ_computed,i - ∇φ_exact,i||

**Relative error:**
E_rel = E_L2 / ||∇φ_exact||_L2

**Component-wise error:**
E_x, E_y, E_z (for directional bias analysis)

**Regime-stratified error:**
E_high, E_trans, E_low (error within each z-regime separately)

### 5.2 Robustness Metrics

**Condition number:**
For LSQ-based methods, track condition number of local reconstruction matrix:
κ = ||A|| × ||A^(-1)||

Report: mean(κ), max(κ), fraction of cells with κ > 10³

**Convergence behavior:**
For implicit methods: iteration count, residual reduction rate

**Failure detection:**
Flag cells where:
- Gradient magnitude > 10 × theoretical max (oscillation)
- Gradient direction error > 90° (wrong sign)
- Reconstruction matrix is singular (κ > 10^6)

### 5.3 Economic Metrics

**Implementation effort:**
- Lines of code per scheme
- Development time (person-hours)
- Debugging complexity (subjective 1-5 scale)

**Computational cost:**
- CPU time per cell per gradient evaluation
- Memory per cell (bytes)
- Total runtime for full test case

**Tuning effort:**
- For hybrid schemes: number of parameter values tested
- Person-hours to select optimal parameters
- Sensitivity: how much does error change with ±20% parameter variation?

### 5.4 Data Collection Automation

**Output format (per test run):**

```json
{
  "test_id": "skew_50deg_GLSQ_alpha0.5_primary",
  "mesh": "skew_50deg.cgns",
  "scheme": "GLSQ",
  "parameters": {"alpha": 0.5},
  "test_function": "primary",
  "z_statistics": {
    "mean": 3.4,
    "std": 0.1,
    "percentiles": [3.3, 3.4, 3.5],
    "f_high": 0.0,
    "f_trans": 1.0,
    "f_low": 0.0
  },
  "errors": {
    "L2": 0.0082,
    "Linf": 0.023,
    "relative": 0.041,
    "by_component": [0.007, 0.009, 0.008],
    "by_regime": {"high": null, "trans": 0.0082, "low": null}
  },
  "robustness": {
    "mean_condition_number": 45.2,
    "max_condition_number": 203.1,
    "ill_conditioned_fraction": 0.003,
    "failed_cells": 0
  },
  "performance": {
    "cpu_seconds": 0.34,
    "memory_mb": 12.5
  },
  "timestamp": "2026-03-10T14:23:11Z"
}
```

**Database:** SQLite for query flexibility, CSV export for plotting

---

## 6. Success Criteria

### 6.1 Hypothesis H1: Phase Transition Existence

**Test:** Plot hybrid advantage ratio R = E_pure / E_hybrid vs z-value across skewness sequence.

**Success criteria:**
- R shows a clear peak in 3 < z < 6 range
- Peak R > 5 (at least 5× advantage)
- R < 2 outside the transition band (z > 6 or z < 3)

**Quantitative metric:**
Peak sharpness S = (R_max - R_baseline) / Δz_peak

where Δz_peak is width of region where R > 3.

**Pass threshold:** S > 2.0 (peak is localized, not broad)

### 6.2 Hypothesis H2: Regime Classification

**Test:** For each production mesh:
1. Compute z-field, classify regimes
2. Select schemes per filter protocol (Cases A/B/C/D)
3. Measure solution error on flow physics case
4. Compare to error from exhaustive scheme testing

**Success criteria:**
- Filtered workflow error < 1.05 × exhaustive error (within 5%)
- Implementation effort reduction > 60% (measured in LOC or person-hours)
- Test run reduction > 70% (number of configurations tested)

**Pass threshold:** All three criteria met simultaneously

### 6.3 Hypothesis H3: Threshold Universality

**Test:** Compute optimal z-thresholds separately for:
- Primary vs secondary vs tertiary test functions
- 2D vs 3D meshes
- Different element types (hex, tet, prism, pyramid)

**Success criteria:**
- Optimal z_low threshold varies by < 50% across cases (2.0 < z_low < 4.5)
- Optimal z_high threshold varies by < 50% across cases (4.5 < z_high < 9.0)

**Pass threshold:** Coefficient of variation CV(z_low) < 0.25, CV(z_high) < 0.25

### 6.4 Hypothesis H4: Economic Validation

**Test:** Measure wall-clock time and developer effort for two workflows:

**Workflow A (Exhaustive):**
- Implement 8 schemes
- Test all on 5 mesh types
- Total: 40 runs

**Workflow B (Filtered):**
- Compute z-fields for 5 meshes (pre-filter)
- Implement 3 schemes (regime-specific)
- Test selected schemes on relevant meshes only
- Total: 12 runs

**Success criteria:**
- Workflow B total time < 0.35 × Workflow A time (65% reduction)
- Workflow B achieves same "optimal" scheme choice in 4/5 meshes

**Pass threshold:** Time reduction > 60%, optimal choice match > 75%

### 6.5 Hypothesis H5: Low-z Collapse

**Test:** On meshes with z < 3 (e.g., 80° skewness):
- Apply all second-order schemes
- Measure relative error: E_rel = E_L2 / ||∇φ||

**Success criteria:**
- All second-order schemes show E_rel > 0.5 (50% error)
- No scheme reduces error below E_rel = 0.3
- First-order GG outperforms all second-order schemes

**Pass threshold:** Min(E_rel over all 2nd-order schemes) > 0.4

---

## 7. Data Collection and Analysis

### 7.1 Experiment Matrix

**Phase 1: Controlled Tests**

| Test Function | Meshes | Schemes | Parameters | Total Runs |
|--------------|---------|---------|------------|------------|
| Primary      | 13      | 6       | 3 (hybrids)| 96         |
| Secondary    | 5 (subset) | 6    | 3          | 48         |
| Tertiary     | 5 (subset) | 6    | 3          | 48         |

**Subtotal Phase 1:** 192 runs

**Phase 2: Production Tests**

| Mesh | Schemes | Test Cases | Total Runs |
|------|---------|------------|------------|
| Flat plate | 4 (filtered) | 1 | 4 |
| Cylinder | 4 (filtered) | 1 | 4 |
| Channel | 6 (comprehensive) | 1 | 6 |

**Subtotal Phase 2:** 14 runs

**Phase 3: Generalization**

| Variation | Meshes | Schemes | Total Runs |
|-----------|--------|---------|------------|
| 2D vs 3D | 4 | 4 | 16 |
| Element types | 6 | 4 | 24 |

**Subtotal Phase 3:** 40 runs

**Phase 4: Economic Comparison**

Workflow A vs B on 5 meshes: ~50 runs total

**Grand Total:** ~300 runs

**Estimated runtime:** 
- Assuming 2 min/run average: 10 hours compute time
- Can parallelize: 2 hours on 5-core workstation

### 7.2 Analysis Pipeline

**Step 1: Raw data ingestion**
- Parse JSON outputs into SQLite database
- Validate completeness (flag missing runs)

**Step 2: Error analysis**
```python
# Generate key plots
plot_error_vs_z(scheme='all', metric='L2')  # Main result
plot_hybrid_advantage_ratio(schemes=['GLSQ', 'Flexible'])
plot_regime_stratified_error()
```

**Step 3: Statistical significance**
- Bootstrap confidence intervals for error ratios
- ANOVA to test significance of z-regime effect
- Tukey HSD for pairwise scheme comparisons within regimes

**Step 4: Threshold calibration**
- Fit piecewise-linear or sigmoid model to error(z) curves
- Identify inflection points as regime boundaries
- Compare to predicted z = 3, z = 6

**Step 5: Economic analysis**
- Compute effort reduction percentages
- Generate decision tree visualization for filter protocol
- Validate Case A/B/C/D classifications

### 7.3 Visualization Requirements

**Key figures for validation paper/report:**

**Figure 1:** Error vs skewness angle for all schemes
- X-axis: θ_skew (degrees)
- Y-axis: L2 error (log scale)
- Lines: one per scheme
- Shaded regions: regime boundaries

**Figure 2:** Hybrid advantage ratio vs z
- X-axis: z-value
- Y-axis: R = E_pure / E_hybrid
- Highlight transition band (3 < z < 6)

**Figure 3:** z-field visualization on production meshes
- Spatial plot colored by z-value
- Three panels: flat plate, cylinder, channel

**Figure 4:** Regime-stratified error distributions
- Box plots: error within high/trans/low regimes
- Grouped by scheme

**Figure 5:** Economic comparison
- Bar chart: Workflow A vs B
- Metrics: time, runs, implementations, final error

**Figure 6:** Condition number vs z
- Scatter plot: each cell as a point
- Color: by regime
- Overlay: schemes as different symbols

---

## 8. Experiment Execution Timeline

### Week 1: Infrastructure Setup
- **Days 1-2:** Mesh generation
  - Generate all 13 controlled skewness meshes
  - Verify quality, compute z-fields
  - Generate metadata reports

- **Days 3-5:** Code implementation
  - Implement 6 gradient schemes
  - Verify on Cartesian test case
  - Set up automation scripts

### Week 2: Phase 1 Execution
- **Days 1-3:** Primary test function (96 runs)
  - Run on controlled meshes
  - Real-time monitoring for failures

- **Days 4-5:** Secondary/tertiary functions (96 runs)
  - Subset of meshes
  - Focus on transition-z band

### Week 3: Phase 2 & 3
- **Days 1-2:** Production mesh generation
  - Flat plate, cylinder, channel

- **Days 3-4:** Production tests (14 runs)
  - Apply filtered workflow
  - Measure solution-level impact

- **Day 5:** Generalization tests (40 runs)
  - 2D/3D comparison
  - Element type variation

### Week 4: Phase 4 & Analysis
- **Days 1-2:** Economic comparison (50 runs)
  - Head-to-head workflow test

- **Days 3-4:** Data analysis
  - Generate all figures
  - Statistical tests
  - Threshold calibration

- **Day 5:** Report generation
  - Assess pass/fail criteria
  - Document findings

### Weeks 5-6 (Optional): Refinement
- Address any failed hypotheses
- Extend to additional test cases if needed
- Prepare publication materials

---

## 9. Automation and AI Integration

### 9.1 Automated Test Harness

**Master control script (Python):**

```python
# experiment_driver.py

class ExperimentDriver:
    def __init__(self, config_file):
        self.config = load_config(config_file)
        self.db = Database('results.db')
        self.mesh_library = MeshLibrary('meshes/')

    def run_full_experiment(self):
        # Phase 1
        for mesh in self.mesh_library.controlled_skewness:
            z_field = compute_z_field(mesh)
            for scheme in self.config.schemes:
                for params in scheme.parameter_space:
                    for test_func in self.config.test_functions:
                        result = self.run_single_test(
                            mesh, scheme, params, test_func
                        )
                        self.db.insert(result)
                        self.generate_progress_report()

        # Phase 2-4 similar structure

    def run_single_test(self, mesh, scheme, params, test_func):
        # Load mesh
        grid = load_mesh(mesh.path)

        # Compute exact gradients
        exact = compute_exact_gradient(test_func, grid.cell_centers)

        # Run scheme
        computed = scheme.compute_gradient(grid, test_func, params)

        # Compute errors
        errors = compute_error_metrics(computed, exact, grid.z_field)

        # Package results
        return ExperimentResult(
            mesh=mesh.name,
            scheme=scheme.name,
            parameters=params,
            errors=errors,
            robustness=compute_robustness_metrics(scheme, grid),
            performance=measure_performance(scheme)
        )
```

**Parallel execution:**
```python
from multiprocessing import Pool

def parallel_experiment(test_list, n_cores=5):
    with Pool(n_cores) as pool:
        results = pool.map(run_single_test, test_list)
    return results
```

### 9.2 AI Assistant Integration Points

**1. Mesh quality pre-analysis:**
```
User: "I just generated flat_plate.cgns. Should I test all schemes?"
AI: "Computing z-field... 72% high-z, 23% transition-z, 5% low-z. 
     Classification: Case B (transition-zone dominant).
     Recommendation: Implement LSQ baseline + GLSQ hybrid.
     Skip pure GG, weighted variants. Expected effort reduction: 65%."
```

**2. Anomaly detection:**
```
AI: "Warning: Test skew_60deg_LSQ_primary shows error 3× higher than 
     predicted for z=2.8. Possible causes:
     1. Mesh generation error (verify skewness uniformity)
     2. Implementation bug (check LSQ matrix construction)
     3. Test function evaluation error
     Running diagnostics..."
```

**3. Adaptive experiment design:**
```
AI: "Results show transition band is narrower than expected (2.5 < z < 4.5).
     Recommendation: Generate 3 additional meshes at θ = 52°, 57°, 62°
     to improve resolution in peak region. Generate meshes?"
User: "Yes"
AI: [generates meshes, adds to test queue]
```

**4. Real-time analysis:**
```
AI: "After 120/192 Phase 1 runs:
     - H1 (phase transition): PASSING (peak R = 7.2 at z = 3.1)
     - H5 (low-z collapse): PASSING (all E_rel > 0.52 for z < 2.5)
     - Estimated completion: 45 minutes
     - Confidence: 95% that remaining runs won't change conclusions"
```

### 9.3 Failure Handling and Recovery

**Automatic retry logic:**
```python
def robust_run(test, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = run_single_test(test)
            if result.is_valid():
                return result
        except Exception as e:
            log_error(test, e, attempt)
            if attempt < max_retries - 1:
                fix_common_issues(test, e)

    mark_as_failed(test)
    alert_user(test)
```

**Common failure modes:**
- Mesh loading errors: verify file integrity, re-export from generator
- Singular matrices in LSQ: reduce to first-order or flag cell
- Memory errors: reduce problem size or increase swap
- Timeout: increase limit or investigate infinite loop

---

## 10. Contingency Plans

### 10.1 If H1 Fails (No Phase Transition)

**Scenario:** Hybrid advantage increases monotonically with skewness, no peak.

**Implications:** z-metric still useful but framework needs revision.

**Actions:**
1. Re-analyze as continuous rather than discrete regime classification
2. Develop interpolation formula: optimal α(z) for hybrid schemes
3. Economic benefit shifts to "auto-tuning" rather than "regime filtering"
4. Update technical note with corrected model

**Timeline impact:** +1 week for re-analysis and revised framework

### 10.2 If H2 Fails (Filter Under-Performs)

**Scenario:** Filtered workflow misses optimal scheme, achieves <90% of exhaustive accuracy.

**Possible causes:**
1. z-metric incomplete (missing mesh quality dimensions)
2. Thresholds need case-specific calibration
3. Production meshes have multi-regime spatial variation not captured by global statistics

**Actions:**
1. Develop multi-dimensional quality metric: z_multi = f(skewness, stretching, non-convexity)
2. Implement spatial adaptation: different schemes in different mesh regions
3. Add "uncertainty flag": when mesh has broad z-distribution, recommend testing 2 scheme classes

**Timeline impact:** +1-2 weeks for enhanced filter development

### 10.3 If H3 Fails (Thresholds Not Universal)

**Scenario:** Optimal z-thresholds vary by >50% between cases.

**Implications:** Framework is case-specific, not a universal pre-filter.

**Actions:**
1. Cluster test cases by similarity (mesh type, flow physics)
2. Develop lookup table: thresholds by application category
3. Machine learning approach: train classifier on mesh+physics features → optimal scheme

**Timeline impact:** +2 weeks for classification system development

### 10.4 If Multiple Hypotheses Fail

**Scenario:** Fundamental issues with z-metric or phase-transition concept.

**Scientific response:**
1. Document negative result (valuable for community)
2. Conduct exploratory data analysis: are there *any* predictive geometric features?
3. Literature review: what did we miss from prior work?

**Alternative frameworks to explore:**
- Spectral analysis of reconstruction matrices
- Information-theoretic measures (mutual information between mesh geometry and gradient accuracy)
- Purely empirical clustering (unsupervised learning on (mesh features, optimal scheme) pairs)

**Timeline impact:** Experiments still valuable; interpretation shifts to "what doesn't work and why"

---

## 11. Appendices

### Appendix A: Software Requirements

**Core dependencies:**
- Python 3.9+ (automation, analysis)
- NumPy, SciPy (numerical computations)
- Matplotlib, Seaborn (visualization)
- pandas (data management)
- SQLite (database)

**Mesh generation:**
- Gmsh 4.8+ (controlled mesh generation)
- OR OpenFOAM blockMesh + transformations

**CFD framework (choose one):**
- OpenFOAM 9+ (if using Option B implementation)
- SU2 7.3+ (alternative)
- Custom C++ + Eigen 3.4 (if using Option C)

**Optional:**
- ParaView (3D visualization of z-fields)
- Jupyter notebooks (interactive analysis)
- Git + LFS (version control for meshes)

### Appendix B: Compute Resources

**Minimum:**
- 4-core CPU (Intel i5 or equivalent)
- 16 GB RAM
- 50 GB disk space
- ~20 hours total compute time

**Recommended:**
- 8-core CPU (allows parallel execution)
- 32 GB RAM (handle large production meshes)
- 100 GB SSD
- ~4 hours total compute time

**Cloud alternative:**
- AWS c5.2xlarge instance (8 vCPU, 16 GB)
- Estimated cost: $50-100 for full experiment
- Use spot instances for 70% cost reduction

### Appendix C: Mesh Quality Formulas

**Skewness (face-based):**

θ_skew,f = arccos(|n_f · d_ij| / |d_ij|)

where:
- n_f = face normal (unit vector)
- d_ij = vector from cell i center to neighbor j center

**Skewness (cell-based):**

θ_skew,i = max(θ_skew,f) over all faces of cell i

**Aspect ratio:**

AR = max_dimension / min_dimension

For hex: ratio of longest to shortest edge  
For tet: ratio of circumradius to inradius × 3

**Non-orthogonality:**

Non-ortho = max(90° - θ_skew, 0)

Range: [0°, 90°], where 0° is perfect orthogonality

**z-metric (complete formula):**

z = (θ_crit / θ_skew) × p × f_connectivity

where:
- θ_crit = 85° (calibrated critical angle)
- θ_skew = cell maximum skewness
- p = scheme accuracy order (1 or 2)
- f_connectivity = min(N_neighbors / N_required, 1.0)
  - For 3D: N_required = 3 (minimum for gradient reconstruction)
  - Penalizes cells with insufficient stencil

### Appendix D: Error Analysis Formulas

**L2 norm:**

||∇φ||_L2 = sqrt[Σ_i V_i ||∇φ_i||²] / sqrt[Σ_i V_i]

(volume-weighted for consistency with FVM integration)

**Order of accuracy (from mesh refinement):**

p = log(E_coarse / E_fine) / log(h_coarse / h_fine)

Expected: p ≈ 2 for second-order schemes on good meshes

**Hybrid advantage ratio:**

R(z) = E_pure(z) / E_hybrid(z)

where E_pure = max(E_LSQ, E_GG) at each z-value

**Peak detection (for H1 validation):**

z_peak = argmax_z R(z)  
R_peak = max_z R(z)  
Δz_FWHM = width where R > 0.5 × R_peak

(full width at half maximum, measures peak sharpness)

### Appendix E: Data Sharing and Reproducibility

**Public repository contents:**
```
gradient-reconstruction-validation/
├── README.md (experiment overview)
├── meshes/ (all test meshes, ~500 MB)
├── src/ (gradient scheme implementations)
├── scripts/ (automation, analysis)
├── results/ (raw data, SQLite database)
├── figures/ (all generated plots)
├── docs/ (this protocol, technical note)
└── LICENSE (MIT or CC-BY-4.0)
```

**DOI registration:** Zenodo for permanent archival

**Reproduction instructions:**
```bash
# Clone repository
git clone https://github.com/zfifteen/gradient-validation.git

# Install dependencies
pip install -r requirements.txt

# Run full experiment (or subset)
python experiment_driver.py --config configs/full_experiment.yaml

# Generate analysis report
python analyze_results.py --output report.pdf
```

**Expected reproduction time:** 6-8 hours on recommended hardware

### Appendix F: Ethical Considerations

**Open science commitment:**
- All code, data, and meshes publicly available
- Negative results published (even if hypotheses fail)
- No p-hacking or selective reporting

**Computational resource efficiency:**
- Optimize code before large-scale runs
- Use early stopping if trends are clear
- Share learned parameters to avoid duplicate effort by others

**AI transparency:**
- Document all AI assistant interactions that influenced experimental design
- Distinguish AI-generated content from human analysis
- Provide full prompt logs if AI writing tools used for documentation

---

## Summary Checklist

Before declaring experiment complete, verify:

- [ ] All 300+ planned runs executed successfully
- [ ] Database integrity check passed (no missing data)
- [ ] All 5 hypotheses evaluated (pass/fail documented)
- [ ] Statistical significance tests completed
- [ ] All 6 key figures generated
- [ ] Economic metrics computed (effort reduction %)
- [ ] Contingency plan activated if needed
- [ ] Results reproducible by independent party
- [ ] Code and data published with DOI
- [ ] Technical note updated with findings
- [ ] AI assistant integration validated

**Final deliverable:** Validation report with clear verdict on z-framework viability and calibrated selection filter tool.

---

**End of Experimental Protocol**

*This document is a living protocol. Update as experiment proceeds and new insights emerge.*
