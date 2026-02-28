# A Multiplicative Conductivity-Memory Gate for Electromagnetic-Gravity-Wave Coupling in the Ionosphere-Troposphere System

## Abstract
Solar electromagnetic (EM) events (flares and high-speed solar-wind streams) create transient ionospheric conductivity enhancements that persist for about 3-10 hours after forcing weakens. This persistence acts as a one-way memory gate that multiplicatively amplifies ionospheric responses to subsequently arriving tropospheric gravity waves (GWs). We define a coupling intensity,
Lambda = r_sigma(t) x (E_GW/E_0),
with three regimes: sub-threshold (Lambda < 1), linear multiplicative (1 <= Lambda <= 3), and nonlinear amplified (Lambda > 3). This timing-dependent, asymmetric interaction explains why moderate solar and moderate weather disturbances can jointly produce stronger responses than isolated strong drivers. It also provides a physical basis for the solar-activity correction term in the Schumann-resonance heuristic model of Nickolaenko (2026). We provide explicit functional forms for the memory kernel M(t) and testable statistical predictions using SZIGO vertical electric-field records, GNSS TEC, and public flare and GW-proxy data.

**Keywords:** ionospheric conductivity, gravity waves, solar-terrestrial coupling, Schumann resonance, priming window, multiplicative coupling

## 1. Introduction
- Brief recap of Nickolaenko (2026) on Schumann-resonance frequency and solar activity.
- Statement of the core puzzle: most frameworks treat EM and mechanical drivers as additive.
- Main claim of this note: a one-way multiplicative priming window with 3-10 h conductivity memory.
- Paper roadmap.

## 2. Physical Basis of the Priming Window
### 2.1 Fast EM driver to conductivity anomaly
Flares, HSS-driven forcing, and particle precipitation rapidly increase effective ionospheric conductivity.

### 2.2 Microphysics of persistence
Ion-neutral recombination and plasma transport produce memory timescales of tau about 4-8 h.

### 2.3 Slow mechanical driver
Upward-propagating tropospheric GW packets typically have 6-24 h transit times to ionospheric altitudes.

### 2.4 Asymmetric cross-channel modulation
The coupling is effectively one-way over event timescales: EM preconditions the ionosphere; GW forcing reads out that state.

### 2.5 Dimensionless coupling intensity
Define Lambda and separate observed behavior into sub-threshold, linear multiplicative, and nonlinear amplified regimes.

**Figure 1:** EM-GW timeline schematic.  
**Figure 2:** Lambda-regime response curve.

## 3. Explicit Forecasting Operator
### 3.1 Conditional response form
delta_observable = EM_term + M(t) x GW_term

### 3.2 Memory kernel parameterization
M(t) = 1 + A exp(-(t - t_EM)/tau)

### 3.3 Embedding in whole-atmosphere models
Outline insertion points for TIE-GCM, GAIA, and WACCM-X style frameworks.

**Figure 3:** Modulation kernel M(t) for representative tau values in the 4-8 h range.

## 4. Observational Support and Testable Predictions
### 4.1 Evidence synthesis
Summarize relevant observational support: HSS and precipitation links, flare-driven conductivity persistence, and GW-TEC variability.

### 4.2 Statistical test design
Run superposed-epoch analysis of GW events stratified by lag to prior solar EM trigger.

### 4.3 Quantitative prediction
Expect about 2-4x enhancement in DeltaTEC and Deltaf1 for events inside vs outside the priming window.

**Figure 4:** Predicted superposed-epoch composites.  
**Figure 5:** Example event from SZIGO 1994-2009 archive (or a labeled placeholder).

## 5. Implications and Future Work
- Better space-weather forecasting skill under moderate forcing conditions.
- Refinement of the Nickolaenko (2026) heuristic model to hourly resolution.
- Broader relevance for whole-atmosphere coupling and climate-space-weather link studies.
- Recommended coordinated campaigns (SZIGO + GNSS + ERA5 GW-flux proxies).

## 6. Conclusions
Conclude with the shift from additive forcing to conditional multiplicative coupling and its forecasting implications.

## References
Use the cleaned bibliography from `evidence.md` plus Nickolaenko (2026).

## Supplementary Material
- Full evidence compilation (`evidence.md`).
- Python scripts for Lambda calculation and event binning.
