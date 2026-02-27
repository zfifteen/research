#!/usr/bin/env python3
"""
Geometric Pump Demonstration (Python "White Paper")
===================================================

Abstract
--------
This script demonstrates a single, testable principle:

    Large force magnitude does not imply net transport if the drive cycle is
    time-reversible (reciprocal). Net transport requires a non-reciprocal cycle,
    i.e., a loop in control-parameter space.

We show this using a standard toy system from ratchet / pump physics:
an overdamped particle in a periodic potential U(x; A, phi) whose parameters
are modulated in time.

Guardrails (read this first)
----------------------------
- This is a *transport pump* toy model, not a propulsion proof.
- It does NOT show reactionless thrust.
- It shows why "static force magnitude" is often the wrong optimization target
  when the actual question is "what does a drive cycle do over a full reset?"

Model (dimensionless)
---------------------
Overdamped Langevin dynamics:

    dx/dt = - dU/dx + sqrt(2*T) * xi(t)

where xi(t) is unit white noise, T is a dimensionless noise strength (kT),
and gamma is set to 1.

Potential (periodic in x with period L=1):
    U(x; A, phi) = A * cos(2*pi*x + phi)

So:
    dU/dx = -A * (2*pi) * sin(2*pi*x + phi)

Protocols
---------
All protocols share the same time base (period = 1 cycle). We compare:

1) RECIPROCAL (1-parameter):
       A(t) varies, phi(t) fixed.
   Control path in (A,phi) is a line segment (encloses zero area).
   Expected drift per cycle: ~0

2) LOOP (2-parameter, non-reciprocal):
       A(t) and phi(t) vary in quadrature, tracing a loop in (A,phi).
   Expected drift per cycle: nonzero

3) LOOP_REVERSED:
       Same loop but opposite orientation (winding flips).
   Expected: drift changes sign.

Metrics
-------
We report:
    - mean drift per cycle (unwrapped displacement / cycles)
    - standard error (SEM) across independent runs

We also produce plots:
    - trajectory.png: example x(t) for reciprocal vs loop
    - drift_summary.png: mean drift per cycle with SEM
    - parameter_loop.png: the control path in (A,phi) space

Reproducibility
---------------
Randomness is controlled via explicit seeds derived from a printed base seed.
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from pathlib import Path

# -------------------------------
# Configuration (edit for your post)
# -------------------------------

@dataclass(frozen=True)
class Config:
    # Numerical integration
    cycles: int = 200                 # number of drive cycles per run
    steps_per_cycle: int = 200        # time steps per cycle
    dt: float = 1.0 / 200.0           # period=1 => dt = 1/steps_per_cycle

    # Potential / drive
    A0: float = 1.0                   # baseline potential amplitude
    dA: float = 0.8                   # amplitude modulation depth (A(t) = A0 + dA*sin(...))
    phi0: float = 0.0                 # baseline phase
    dphi: float = 2.0                 # phase modulation depth (radians), for loop protocols

    # Noise strength (dimensionless "temperature")
    T: float = 0.25                   # noise helps hopping; set small->more stuck, large->more diffusion

    # Sampling / statistics
    runs: int = 40                    # independent runs for mean/SEM
    burn_in_cycles: int = 20          # exclude early transient cycles from drift statistics

    # Output
    out_dir: str = "pump_demo_outputs"
    seed0: int = 1337                 # base seed

CFG = Config()

# -------------------------------
# Core physics helpers
# -------------------------------

TWO_PI = 2.0 * np.pi

def dU_dx(x: float, A: float, phi: float) -> float:
    """d/dx of U(x;A,phi) = A*cos(2*pi*x + phi) with period 1 in x."""
    return -A * TWO_PI * np.sin(TWO_PI * x + phi)

def protocol(t: np.ndarray, kind: str, cfg: Config) -> tuple[np.ndarray, np.ndarray]:
    """
    Return A(t), phi(t) for the chosen drive protocol.
    Period is 1 in dimensionless time, so sin(2*pi*t) completes one cycle.
    """
    s = np.sin(TWO_PI * t)
    c = np.cos(TWO_PI * t)

    if kind == "reciprocal":
        # 1-parameter drive: line segment in (A,phi) -> encloses zero area.
        A = cfg.A0 + cfg.dA * s
        phi = np.full_like(t, cfg.phi0)
        return A, phi

    if kind == "loop":
        # 2-parameter drive: loop in (A,phi) space (sin/cos in quadrature).
        A = cfg.A0 + cfg.dA * s
        phi = cfg.phi0 + cfg.dphi * c
        return A, phi

    if kind == "loop_reversed":
        # Same loop with opposite winding (orientation flipped).
        A = cfg.A0 + cfg.dA * s
        phi = cfg.phi0 - cfg.dphi * c
        return A, phi

    raise ValueError(f"Unknown protocol kind: {kind}")

def simulate_one_run(rng: np.random.Generator, kind: str, cfg: Config) -> dict:
    """Simulate one run and return time series and per-cycle drift stats."""
    total_steps = cfg.cycles * cfg.steps_per_cycle
    t = np.arange(total_steps) * cfg.dt  # [0, cycles) since period=1

    A_t, phi_t = protocol(t % 1.0, kind=kind, cfg=cfg)

    # Unwrapped position
    x = np.zeros(total_steps + 1)

    # Euler–Maruyama for overdamped Langevin dynamics
    noise_scale = np.sqrt(2.0 * cfg.T * cfg.dt)
    for i in range(total_steps):
        x[i + 1] = (
            x[i]
            - dU_dx(float(x[i]), float(A_t[i]), float(phi_t[i])) * cfg.dt
            + noise_scale * rng.normal()
        )

    # Per-cycle displacements
    x_cycle = x[::cfg.steps_per_cycle]
    d_cycle = np.diff(x_cycle)

    # Exclude burn-in cycles
    start = min(cfg.burn_in_cycles, len(d_cycle))
    d_use = d_cycle[start:]
    drift_mean = float(np.mean(d_use)) if len(d_use) else float("nan")

    return {
        "t": t,
        "A_t": A_t,
        "phi_t": phi_t,
        "x": x[1:],        # align with t
        "d_cycle": d_cycle,
        "drift_mean": drift_mean,
    }

def run_ensemble(kind: str, cfg: Config) -> dict:
    """Run multiple independent simulations and compute mean and SEM of drift per cycle."""
    drifts = []
    for r in range(cfg.runs):
        seed = cfg.seed0 + 10_000 * (hash(kind) % 997) + r
        rng = np.random.default_rng(seed)
        out = simulate_one_run(rng, kind=kind, cfg=cfg)
        drifts.append(out["drift_mean"])

    drifts = np.array(drifts, dtype=float)
    mean = float(np.nanmean(drifts))
    sem = float(np.nanstd(drifts, ddof=1) / np.sqrt(np.sum(~np.isnan(drifts))))
    return {"kind": kind, "drifts": drifts, "mean": mean, "sem": sem}

def detectable(mean: float, sem: float) -> bool:
    """Heuristic 'detectable' check: |mean| > 3*SEM."""
    return abs(mean) > 3.0 * sem if np.isfinite(sem) and sem > 0 else False

# -------------------------------
# Main: run, print, plot
# -------------------------------

def main() -> None:
    out_dir = Path(CFG.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Geometric Pump Demonstration")
    print("=" * 30)
    print("Claim shown by this script:")
    print("  (1) Reciprocal (1-parameter) cycling -> ~0 net drift per cycle")
    print("  (2) Non-reciprocal (2-parameter loop) -> nonzero drift; sign flips with loop orientation")
    print()
    print("Guardrail: This is a transport toy model. It does NOT prove propulsion.")
    print()

    # Assumption ledger
    print("Assumption ledger (dimensionless):")
    for k, v in CFG.__dict__.items():
        print(f"  {k:>16s} = {v}")
    print()

    # Run ensembles
    kinds = ["reciprocal", "loop", "loop_reversed"]
    results = [run_ensemble(k, CFG) for k in kinds]

    # Print results table
    print("Results: drift per cycle (mean ± SEM across runs)")
    print("-" * 54)
    for r in results:
        print(f"  {r['kind']:<14s} : {r['mean']:+.5f} ± {r['sem']:.5f}")
    print("-" * 54)

    rec = next(r for r in results if r["kind"] == "reciprocal")
    loo = next(r for r in results if r["kind"] == "loop")
    rev = next(r for r in results if r["kind"] == "loop_reversed")

    print()
    print("Interpretation checks (simple heuristics):")
    print(f"  reciprocal: detectable drift? {detectable(rec['mean'], rec['sem'])} (expect False)")
    print(f"  loop:       detectable drift? {detectable(loo['mean'], loo['sem'])} (expect True)")
    print(f"  reversed:   sign flip?         {np.sign(loo['mean']) == -np.sign(rev['mean'])} (expect True)")
    print()

    # Tweet-ready footer (copy/paste)
    print("Tweet-ready takeaway:")
    print("  If the control cycle is time-reversible, you get ~0 net after reset (big forces don't help).")
    print("  A 2-parameter loop in control space produces net transport, and reversing the loop flips the sign.")
    print("  That's the 'cycle geometry / winding' point — not a propulsion proof.")
    print()

    # Example trajectories (same seed for fair visual comparison)
    example_seed = CFG.seed0 + 424242
    ex_rec = simulate_one_run(np.random.default_rng(example_seed), "reciprocal", CFG)
    ex_loop = simulate_one_run(np.random.default_rng(example_seed), "loop", CFG)

    # 1) Trajectory plot
    plt.figure()
    plt.plot(ex_rec["t"], ex_rec["x"], label="reciprocal (1-parameter)")
    plt.plot(ex_loop["t"], ex_loop["x"], label="loop (2-parameter)")
    plt.xlabel("time [cycles]")
    plt.ylabel("unwrapped position x(t)")
    plt.title("Toy demonstration: reciprocal vs loop driving")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "trajectory.png", dpi=200)

    # 2) Drift summary plot (with a zero line + clearer labels + values)
    plt.figure()
    labels = ["reciprocal", "loop", "loop (reversed)"]
    means = [rec["mean"], loo["mean"], rev["mean"]]
    sems  = [rec["sem"],  loo["sem"],  rev["sem"]]
    x = np.arange(len(labels))
    plt.bar(x, means, yerr=sems, capsize=6)
    plt.axhline(0.0, linestyle="--", linewidth=1)
    plt.xticks(x, labels, rotation=10)
    plt.ylabel("mean drift per cycle")
    plt.title("Net transport depends on cycle geometry (loop orientation matters)")
    plt.text(0.02, 0.98, f"n={CFG.runs} runs, error bars=SEM", transform=plt.gca().transAxes,
             ha="left", va="top")
    # value labels
    for i, (m, s) in enumerate(zip(means, sems)):
        plt.text(i, m + np.sign(m)*0.02, f"{m:+.3f}", ha="center", va="bottom" if m >= 0 else "top")
    plt.tight_layout()
    plt.savefig(out_dir / "drift_summary.png", dpi=200)

    # 3) Parameter-space path plot (A, phi)
    t_short = np.linspace(0.0, 1.0, 800, endpoint=False)
    A_rec, phi_rec = protocol(t_short, "reciprocal", CFG)
    A_loop, phi_loop = protocol(t_short, "loop", CFG)
    A_rev,  phi_rev  = protocol(t_short, "loop_reversed", CFG)

    plt.figure()
    plt.plot(A_rec, phi_rec, label="reciprocal (line: no enclosed area)")
    plt.plot(A_loop, phi_loop, label="loop (non-reciprocal)")
    plt.plot(A_rev,  phi_rev,  label="loop (reversed winding)")
    plt.xlabel("A(t)")
    plt.ylabel("phi(t) [rad]")
    plt.title("Control path in parameter space: line vs loop (winding)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "parameter_loop.png", dpi=200)

    print(f"Saved plots to: {out_dir.resolve()}")
    print("  - trajectory.png")
    print("  - drift_summary.png")
    print("  - parameter_loop.png")

if __name__ == "__main__":
    main()
