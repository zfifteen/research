#!/usr/bin/env python3
"""
Geometric Pump Demonstration (Python "White Paper")
===================================================

Abstract
--------
This script demonstrates a single point:

    Large force magnitude does not imply net transport if the drive cycle is
    time-reversible (reciprocal). Net transport requires a non-reciprocal cycle,
    i.e., a loop in control-parameter space.

We show this with a standard toy system used in ratchet/pump literature:
an overdamped particle in a periodic potential U(x; A, phi) whose parameters
are modulated in time.

This is NOT a propulsion proof.
-------------------------------
This is a minimal, falsifiable demonstration of a *cycle-geometry* principle:
    - 1-parameter (reciprocal) driving -> ~0 net drift per cycle
    - 2-parameter loop driving -> nonzero drift per cycle, sign flips with loop orientation

If someone claims a physical system can produce net impulse, this demo explains
why "static force magnitude" is the wrong optimization target and why the drive
protocol (cycle structure) is the meaningful variable to test.

Model
-----
We simulate overdamped Langevin dynamics (dimensionless units):

    dx/dt = - dU/dx + sqrt(2*T) * xi(t)

where xi(t) is unit white noise, T is a dimensionless noise strength (kT),
and gamma is set to 1.

Potential (periodic in x with period L=1):
    U(x; A, phi) = A * cos(2*pi*x + phi)

So:
    dU/dx = -A * (2*pi) * sin(2*pi*x + phi)

Protocols
---------
We compare three protocols, all with the same time base:
1) RECIPROCAL (1-parameter): A(t) varies, phi(t) fixed.  -> expected drift ~ 0
2) LOOP (2-parameter):       A(t) and phi(t) trace a loop -> expected drift != 0
3) LOOP_REVERSED:            same loop but reversed orientation -> drift sign flips

Metrics
-------
We report:
    - mean drift per cycle (unwrapped displacement / cycles)
    - standard error across independent runs (SEM)
We also generate plots:
    - example trajectory x(t)
    - drift per cycle summary (with error bars)
    - control-parameter path in (A, phi) space

Reproducibility
---------------
All randomness is controlled by explicit seeds printed to the terminal.
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

def dU_dx(x: np.ndarray, A: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """
    Spatial derivative of U(x;A,phi) = A*cos(2*pi*x + phi).
    Note: We use dimensionless x with period 1.
    """
    return -A * TWO_PI * np.sin(TWO_PI * x + phi)

def protocol(t: np.ndarray, kind: str, cfg: Config) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns A(t), phi(t) for the chosen drive protocol.
    Period is 1 in dimensionless time, so sin(2*pi*t) completes one cycle.
    """
    s = np.sin(TWO_PI * t)
    c = np.cos(TWO_PI * t)

    if kind == "reciprocal":
        # 1-parameter drive: A changes, phase fixed => reciprocal in control space.
        A = cfg.A0 + cfg.dA * s
        phi = np.full_like(t, cfg.phi0)
        return A, phi

    if kind == "loop":
        # 2-parameter drive: loop in (A,phi) space (sin/cos quadrature).
        A = cfg.A0 + cfg.dA * s
        phi = cfg.phi0 + cfg.dphi * c
        return A, phi

    if kind == "loop_reversed":
        # Same loop with reversed orientation => should flip drift sign.
        A = cfg.A0 + cfg.dA * s
        phi = cfg.phi0 - cfg.dphi * c
        return A, phi

    raise ValueError(f"Unknown protocol kind: {kind}")

def simulate_one_run(rng: np.random.Generator, kind: str, cfg: Config) -> dict:
    """
    Simulates one run and returns time series and per-cycle drift stats.
    """
    total_steps = cfg.cycles * cfg.steps_per_cycle
    t = np.arange(total_steps) * cfg.dt  # [0, cycles) since period=1

    A_t, phi_t = protocol(t % 1.0, kind=kind, cfg=cfg)

    x = np.zeros(total_steps + 1)  # unwrapped position
    # Euler-Maruyama
    noise_scale = np.sqrt(2.0 * cfg.T * cfg.dt)

    for i in range(total_steps):
        # Overdamped: dx = -dU/dx * dt + sqrt(2T dt)*N(0,1)
        x[i+1] = x[i] - dU_dx(x[i], A_t[i], phi_t[i]) * cfg.dt + noise_scale * rng.normal()

    # Per-cycle displacements (unwrapped)
    x_cycle = x[::cfg.steps_per_cycle]  # position at each cycle boundary
    d_cycle = np.diff(x_cycle)          # displacement per cycle

    # Exclude burn-in cycles for stats
    start = min(cfg.burn_in_cycles, len(d_cycle))
    d_use = d_cycle[start:]
    drift_mean = float(np.mean(d_use)) if len(d_use) else float("nan")

    return {
        "t": t,
        "A_t": A_t,
        "phi_t": phi_t,
        "x": x[1:],               # align with t
        "d_cycle": d_cycle,
        "drift_mean": drift_mean,
    }

def run_ensemble(kind: str, cfg: Config) -> dict:
    """
    Runs multiple independent simulations and returns mean/SEM of drift per cycle.
    """
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

# -------------------------------
# Main: run, print, plot
# -------------------------------

def main() -> None:
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Geometric Pump Demonstration")
    print("=" * 30)
    print("This script demonstrates:")
    print("  - Reciprocal (1-parameter) cycling -> ~0 net drift per cycle")
    print("  - Non-reciprocal (2-parameter loop) -> nonzero drift; sign flips with loop orientation")
    print()
    print("Guardrail: This is a toy model. It does NOT prove propulsion.")
    print()

    # Print configuration ledger (so the reader can audit assumptions)
    print("Assumption ledger (dimensionless):")
    for k, v in cfg.__dict__.items():
        print(f"  {k:>16s} = {v}")
    print()

    # Run ensembles
    kinds = ["reciprocal", "loop", "loop_reversed"]
    results = [run_ensemble(k, cfg) for k in kinds]

    # Terminal output table
    print("Results: drift per cycle (mean ± SEM across runs)")
    print("-" * 54)
    for r in results:
        print(f"  {r['kind']:<14s} : {r['mean']:+.5f} ± {r['sem']:.5f}")
    print("-" * 54)

    # Simple decision statements
    rec = next(r for r in results if r["kind"] == "reciprocal")
    loo = next(r for r in results if r["kind"] == "loop")
    rev = next(r for r in results if r["kind"] == "loop_reversed")

    # Heuristic "detectable" check: mean is > 3*SEM
    def detectable(mean: float, sem: float) -> bool:
        return abs(mean) > 3.0 * sem if np.isfinite(sem) and sem > 0 else False

    print()
    print("Interpretation checks (simple heuristics):")
    print(f"  reciprocal: detectable drift? {detectable(rec['mean'], rec['sem'])} (expect False)")
    print(f"  loop:       detectable drift? {detectable(loo['mean'], loo['sem'])} (expect True)")
    print(f"  reversed:   sign flip?         {np.sign(loo['mean']) == -np.sign(rev['mean'])} (expect True)")
    print()

    # Produce plots using an example single run for trajectories
    example_seed = cfg.seed0 + 424242
    rng = np.random.default_rng(example_seed)
    ex_rec = simulate_one_run(rng, "reciprocal", cfg)

    rng = np.random.default_rng(example_seed)
    ex_loop = simulate_one_run(rng, "loop", cfg)

    # 1) Trajectory plot
    plt.figure()
    plt.plot(ex_rec["t"], ex_rec["x"], label="reciprocal (1-parameter)")
    plt.plot(ex_loop["t"], ex_loop["x"], label="loop (2-parameter)")
    plt.xlabel("time [cycles]")
    plt.ylabel("unwrapped position x(t)")
    plt.title("Toy demonstration: reciprocal vs loop driving")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "trajectory.png", dpi=180)

    # 2) Drift per cycle summary plot
    plt.figure()
    means = [r["mean"] for r in results]
    sems = [r["sem"] for r in results]
    labels = [r["kind"] for r in results]
    x = np.arange(len(labels))
    plt.bar(x, means, yerr=sems, capsize=6)
    plt.xticks(x, labels, rotation=10)
    plt.ylabel("mean drift per cycle")
    plt.title("Net transport depends on cycle geometry (loop orientation matters)")
    plt.tight_layout()
    plt.savefig(out_dir / "drift_summary.png", dpi=180)

    # 3) Parameter-space path plot (A, phi)
    t_short = np.linspace(0.0, 1.0, 600, endpoint=False)
    A_rec, phi_rec = protocol(t_short, "reciprocal", cfg)
    A_loop, phi_loop = protocol(t_short, "loop", cfg)
    A_rev, phi_rev = protocol(t_short, "loop_reversed", cfg)

    plt.figure()
    plt.plot(A_rec, phi_rec, label="reciprocal (line segment)")
    plt.plot(A_loop, phi_loop, label="loop (non-reciprocal)")
    plt.plot(A_rev,  phi_rev,  label="loop_reversed (opposite winding)")
    plt.xlabel("A(t)")
    plt.ylabel("phi(t) [rad]")
    plt.title("Control path in parameter space: line vs loop (winding)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "parameter_loop.png", dpi=180)

    # Display where outputs went
    print(f"Saved plots to: {out_dir.resolve()}")
    print("  - trajectory.png")
    print("  - drift_summary.png")
    print("  - parameter_loop.png")

if __name__ == "__main__":
    cfg = CFG  # small alias for readability
    main()
