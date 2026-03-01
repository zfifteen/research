# Code Review: `tsz-chronometer`

Date: 2026-03-01  
Review type: Post-remediation verification  
Scope: `protocluster_thermal_clock_whitepaper.py`, `tsz_chronometer_plots.py`

## Status Summary

- Initial findings: 6
- Resolved: 6
- Open: 0

## Findings (Updated Status)

1. **High** - Mass-scaling inconsistency in robustness analysis.  
Status: **Resolved**  
Evidence:
- Added explicit scaling helpers: `virial_radius_from_mass` and `agn_power_from_mass`.
- Section 4 now computes `E_grav(M)` and `t_required(M)` using consistent mass-dependent assumptions.
- Robustness reporting now uses computed factors directly.  
File references:
`protocluster_thermal_clock_whitepaper.py:130`
`protocluster_thermal_clock_whitepaper.py:138`
`protocluster_thermal_clock_whitepaper.py:232`
`protocluster_thermal_clock_whitepaper.py:239`
`protocluster_thermal_clock_whitepaper.py:244`
`protocluster_thermal_clock_whitepaper.py:265`
`protocluster_thermal_clock_whitepaper.py:273`

2. **High** - Circular population validation (kinematics derived directly from `eta`).  
Status: **Resolved**  
Evidence:
- Kinematics are now generated from latent `quiet_fraction` rather than directly from `eta_pop`.
- `eta_pop` remains a derived observable from surplus/power; correlations are no longer hard-coded by construction.  
File references:
`protocluster_thermal_clock_whitepaper.py:343`
`protocluster_thermal_clock_whitepaper.py:349`
`protocluster_thermal_clock_whitepaper.py:361`
`protocluster_thermal_clock_whitepaper.py:366`
`protocluster_thermal_clock_whitepaper.py:370`
`protocluster_thermal_clock_whitepaper.py:374`

3. **Medium** - Script failed in clean directories due to missing `figures/`.  
Status: **Resolved**  
Evidence:
- `os.makedirs("figures", exist_ok=True)` added before figure writes.  
File reference:
`protocluster_thermal_clock_whitepaper.py:434`

4. **Medium** - Figure and metadata written to different locations.  
Status: **Resolved**  
Evidence:
- Figure path is now explicit (`figure_path` in `figures/`).
- Metadata path is now paired with figure (`figure_path + ".meta.json"`).  
File references:
`protocluster_thermal_clock_whitepaper.py:537`
`protocluster_thermal_clock_whitepaper.py:547`

5. **Low** - Robustness caption did not match computed values.  
Status: **Resolved**  
Evidence:
- Caption now computes `% change` and direction from `t_test` at runtime.  
File references:
`tsz_chronometer_plots.py:128`
`tsz_chronometer_plots.py:129`
`tsz_chronometer_plots.py:135`

6. **Low** - Hardcoded p-value labels in annotations/summary.  
Status: **Resolved**  
Evidence:
- Added `format_p_value()` helper and applied it in plots and summary table.  
File references:
`protocluster_thermal_clock_whitepaper.py:146`
`protocluster_thermal_clock_whitepaper.py:492`
`protocluster_thermal_clock_whitepaper.py:503`
`protocluster_thermal_clock_whitepaper.py:562`
`protocluster_thermal_clock_whitepaper.py:618`

## Runtime Verification

1. `python3 tsz_chronometer_plots.py` -> passes; expected figure outputs created.
2. `python3 protocluster_thermal_clock_whitepaper.py` -> passes; figure and paired metadata generated under `figures/`.
3. Clean-directory smoke checks for both scripts -> pass (no pre-existing `figures/` required).
4. Syntax checks: `python3 -m py_compile ...` -> pass.

## Remaining Gaps

1. No automated tests exist yet for numerical invariants (scaling exponents, robustness factor behavior).
2. No automated regression test currently verifies plot annotations remain synchronized with computed values.
3. No CI smoke job currently runs both scripts in a clean temp directory.
