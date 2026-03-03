# PhaseWall at the Gaussian Curvature Boundary: An Exploratory Technical Note

## Abstract
This note evaluates whether the Gaussian curvature transition at `r = σ` can be used as a practical stabilizer for stochastic optimization updates. The method applies a soft radial damping rule in normalized radius space (`r = ||x-μ||/σ`) with a Mahalanobis-radius extension for anisotropic settings. In the reported benchmark artifacts (Sphere, Rosenbrock, Rastrigin), the PhaseWall variant shows lower final objective values than the vanilla baseline under the documented conditions. This release is exploratory: it packages current evidence artifacts and QC traceability, but does not include a full from-scratch rerun pipeline.

## 1. Problem and Scope
### 1.1 Research Question
Can a phase-aware update rule at the Gaussian curvature boundary (`r = σ`) improve robustness and sample efficiency in noisy optimization relative to a vanilla baseline in the reported runs?

### 1.2 Scope Boundaries
In scope:
- Geometric interpretation of the Gaussian surface boundary as a practical update-control heuristic.
- Artifact-backed benchmark comparisons already documented in this repository.

Out of scope:
- Universal claims across all optimizers, tasks, or noise regimes.
- Claims of production-readiness beyond the reported artifacts.
- New empirical results not already present in repository evidence.

## 2. Method
### 2.1 Core Radius Definitions
Isotropic normalized radius:

`r = ||x - μ|| / σ`

Anisotropic extension (Mahalanobis radius):

`r = sqrt((x - μ)^T Σ^-1 (x - μ))`

The method uses this radius to switch behavior between interior and exterior regimes around the boundary at `r = 1` (equivalent to `r = σ` before normalization).

### 2.2 Soft Damping Rule (z-space)
The current mechanism uses soft radial damping on samples outside the boundary:

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

Implementation details and design constraints are documented in:
- `gaussian-hill-surface/docs/specs/PhaseWall_Tech_Spec_v2.1.md`

## 3. Experimental Setup (Reported Artifacts)
This note summarizes existing repository artifacts and does not claim fresh reruns in this revision.

Reported benchmark families:
- Sphere
- Rosenbrock
- Rastrigin

Evaluation details (seed policy, budgets, and run settings) are treated as documented in the benchmark artifacts:
- `gaussian-hill-surface/docs/analysis/benchmarks.md`
- `gaussian-hill-surface/artifacts/reports/PhaseWall_Benchmark_Report.pdf`

## 4. Results (Artifact-Backed)
From `docs/analysis/benchmarks.md`, the reported median comparisons are:

| Function | Vanilla Median | PhaseWall Median | Reported Win Factor |
|---|---:|---:|---:|
| Sphere | 1.2403 | 0.5050 | 2.42x |
| Rosenbrock | 120.2847 | 31.0244 | 3.88x |
| Rastrigin | 40.0756 | 28.8743 | 1.47x |

The same benchmark note also reports a 58/60 run-level win count in the recorded set. These values are presented as reported artifact outcomes under the documented conditions, not as universal performance guarantees.

Supporting artifacts:
- `gaussian-hill-surface/artifacts/reports/PhaseWall_Benchmark_Report.pdf`
- `gaussian-hill-surface/artifacts/figures/benchmarks/benchmark_bars.png`
- `gaussian-hill-surface/artifacts/figures/benchmarks/benchmark_ratios.png`
- `gaussian-hill-surface/artifacts/figures/concepts/img.png`
- `gaussian-hill-surface/artifacts/figures/concepts/img_1.png`

## 5. Limitations and Failure Modes
- This release validates artifact traceability and summary reproducibility checks, not full benchmark regeneration from raw scripts.
- Reported results are limited to currently documented tasks and settings; generalization outside these settings remains unproven.
- Strong performance claims are sensitive to noise regime, parameterization, and implementation details.
- A full rerun package (raw run logs, seed-indexed regeneration scripts) is not yet included in this version.

## 6. Reproducibility
QC reproducibility command (from `QC_CHECKLIST.md`):

```bash
python3 -c "import pathlib; req=[pathlib.Path('gaussian-hill-surface/artifacts/reports/PhaseWall_Benchmark_Report.pdf'), pathlib.Path('gaussian-hill-surface/docs/analysis/benchmarks.md')]; assert all(p.exists() for p in req), 'Missing required reproducibility artifacts'; print('repro smoke pass')"
```

Environment snapshot:
- OS: macOS
- Python: 3.10+
- Check type: artifact integrity + evidence traceability smoke check

Artifact manifest is maintained in:
- `gaussian-hill-surface/QC_CHECKLIST.md`

## 7. Conclusion
In these reported runs, the PhaseWall formulation is associated with lower final objective values than the vanilla baseline on the documented benchmark set. The current evidence supports an exploratory claim that geometry-aware damping may improve robustness under the tested conditions. The next validation step is to add a full rerun pipeline with raw-result regeneration to strengthen reproducibility beyond artifact-level verification.

## References
1. `gaussian-hill-surface/docs/specs/PhaseWall_Tech_Spec_v2.1.md`
2. `gaussian-hill-surface/docs/analysis/benchmarks.md`
3. `gaussian-hill-surface/artifacts/reports/PhaseWall_Benchmark_Report.pdf`
4. `gaussian-hill-surface/README.md`
