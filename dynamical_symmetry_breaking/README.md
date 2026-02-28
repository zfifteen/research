# Dynamical Symmetry Breaking in Legendre Duality

This directory contains an executable theory note showing how Legendre-dual representations become dynamically inequivalent under finite-rate driving.

## Thesis

Classical Legendre duality is exact in the quasi-static limit, where relaxation is effectively complete between perturbations.  
When driving is finite-rate, lag currents appear and dissipation depends on which representation is used.

Key control parameter:

```text
Omega = omega_pert * tau_relax
```

- `Omega << 1`: near-equilibrium, dual descriptions are effectively symmetric.
- `Omega >= 1`: non-adiabatic effects matter, and symmetry breaks dynamically.

## Theory Sketch

1. **Static geometric symmetry**  
   Legendre transform is involutive in equilibrium-like conditions.

2. **Finite-rate correction**  
   Entropy production decomposes as:

   ```text
   Sigma_tot = Sigma_hk + Sigma_na
   ```

   where `Sigma_na` captures excess non-adiabatic dissipation.

3. **Representation-dependent cost**  
   Under finite-rate driving, the lag term projects differently in primal vs dual coordinates.  
   This leads to different dissipation even when both representations describe the same static manifold.

4. **Chemotaxis interpretation**  
   For rapid concentration fluctuations, the concentration-based (primal) representation is cheaper in this model than the chemical-potential-like (dual) representation.

## Figures

### Figure 1: Finite-rate symmetry breaking vs Omega

Shows that representation-dependent dissipation emerges at finite `Omega` and vanishes toward the slow-driving regime.

![Figure 1: Symmetry breaking](figures/whitepaper_fig1_symmetry_breaking.png)

### Figure 2: High-Omega lag separation

Illustrates larger lag amplitude/phase offset in the dual representation at high driving frequency.

![Figure 2: High-Omega lag](figures/whitepaper_fig2_lag.png)

### Figure 3: ATP cost prediction window

Shows model-predicted ATP advantage for the primal representation over `Omega = 5..30`.  
With current parameters, the plotted savings window is approximately `16.8-20.6%` (mean `18.5%`).

![Figure 3: Chemotaxis ATP prediction](figures/whitepaper_fig3_chemotaxis_atp.png)

## Run

From this directory:

```bash
./run_whitepaper.sh
```

This regenerates all three figures under `figures/`.

## Files

- `dynamical_symmetry_breaking.py`: executable white-paper script
- `run_whitepaper.sh`: reproducible runner with local cache settings
- `requirements.txt`: Python dependency pins/ranges
- `figures/`: generated output figures used above
