# Experiment Closeout: Falsified / Stopped

Date: 2026-03-03

## What We Tried

We tested the original hypothesis from Technical Note 2:

- Gradient reconstruction should show a sharp transition behavior controlled by `z`.
- In the transition band (`3 < z < 6`), GLSQ hybrid (`alpha=0.5`) should have a strong advantage (`5-20x`) over pure methods.

Implementation and test harness work was completed in setup_1:

- Gradient methods implemented: GG, WLSQ, GLSQ (`alpha in {0.0, 0.5, 1.0}`).
- Manufactured solution used: `f(x,y) = sin(pi x) cos(pi y)`.
- Metrics computed: volume-weighted L2 error, normalized monotonicity overshoot `|C|_max`, runtime.
- Controlled mesh family and optional mixed mesh were run.

Key artifacts:

- `setup_1/test_gradients.py`
- `setup_1/FINDINGS.md`
- `setup_1/results/2026-03-03_run/validation_report.md`
- `setup_1/results/2026-03-03_run/raw/metrics_long.csv`
- `setup_1/results/2026-03-03_run/raw/summary_by_mesh.csv`

## What We Found

Across the controlled skewness family:

1. WLSQ was the most accurate method on every mesh.
2. GLSQ (`alpha=0.5`) was consistently between WLSQ and GG.
3. Hybrid advantage stayed near ~2x, not 5-20x.
4. The observed peak did not satisfy the original success criterion.

The original hypothesis was therefore marked falsified for this experiment setup.

## Why We Stopped

The original goal depended on demonstrating a strong, narrow hybrid-advantage window.  
The measured results did not support that claim under the current data and protocol.

A revised hypothesis and parallel setup_3 were drafted to continue under new assumptions, but this was intentionally stopped because it no longer serves the original objective.

In short:

- Engineering execution succeeded (harness, runs, artifacts).
- Scientific target for the original hypothesis was not achieved.
- Continuing with revised hypotheses was judged out of scope for the original goal.

## Stop Decision

This experiment line is closed for the original objective.

No further runs are planned unless a new objective is defined (new field, new mesh family, or new success criteria).
