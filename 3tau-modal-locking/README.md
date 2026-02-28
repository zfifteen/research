# 3τ Modal-Locking Threshold

**From Transient Traveling Waves to Efficient Standing-Wave Simulation in 1D Wave Systems**

### Abstract
We introduce the precise causal threshold at which a finite one-dimensional wave system transitions from pure d’Alembert traveling-wave behavior to globally coherent standing-wave modal dynamics: exactly **t = 3τ** (where **τ = L/c** is the domain-crossing time). Before 3τ the boundaries are causally invisible to any observer. After 3τ the entire domain has experienced multiple reflections from both ends, allowing a lossless projection onto the discrete Fourier eigenmodes. This insight enables hybrid algorithms that are mathematically exact yet deliver **5–25× speedups** in real-time audio synthesis, FDTD solvers, and interactive physics engines.

### Key Figures
- **Figure 1**: Exact d’Alembert evolution — clear traveling → standing transition at 3τ
- **Figure 2**: Spectral transition from continuous-like to sharp discrete harmonics
- **Figure 3**: Spatial energy variance stabilizes exactly at the 3τ threshold
- **Figure 4**: Performance: hybrid (FDTD → modal at 3τ) vs pure FDTD

### Repository Contents
- `3tau_modal_locking_whitepaper.py` — self-contained script that prints the full mini-whitepaper and generates all figures
- `figures/` — high-resolution PNGs ready for slides, papers, or GitHub README

### How to Run
```bash
cd 3tau-modal-locking
python3 3tau_modal_locking_whitepaper.py
```
@misc{3tau-modal-locking,
author = {Fate},
title  = {The 3τ Modal-Locking Threshold in 1D Wave Systems},
year   = {2026},
url    = {https://github.com/zfifteen/research/tree/main/3tau-modal-locking},
note   = {Mini whitepaper}
}
