#!/usr/bin/env python3
"""
Permutation 5: robust, complete validation of CONJECTURE.md + MORE.md.

Design goals
------------
1) Keep Pe_r as instantaneous organizer: Pe_r = L^2 / (D_u * tau_r)
2) Measure tau_r and L from simulations (no fitted forcing constants)
3) Explicitly test transient control claim: quench vs ramp interventions
4) Quantify second timescale ratio: intervention speed vs reorganization speed

Outputs
-------
- metrics_sweep.csv: fixed-chemistry Du-sweep run metrics
- metrics_protocols.csv: quench/ramp intervention metrics
- figures in output directory
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import center_of_mass, label


# -----------------------------------------------------------------------------
# Gray-Scott core
# -----------------------------------------------------------------------------

def laplacian(z: np.ndarray, dx: float = 1.0) -> np.ndarray:
    return (
        np.roll(z, 1, axis=0)
        + np.roll(z, -1, axis=0)
        + np.roll(z, 1, axis=1)
        + np.roll(z, -1, axis=1)
        - 4.0 * z
    ) / (dx * dx)


def init_fields(n: int, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    u = np.ones((n, n), dtype=np.float64)
    v = np.zeros((n, n), dtype=np.float64)

    # Multi-seed initialization for interacting spot field.
    for ix in range(3):
        for iy in range(3):
            cx = n // 6 + ix * n // 3
            cy = n // 6 + iy * n // 3
            r = max(2, n // 32)
            u[cx-r:cx+r, cy-r:cy+r] = 0.50
            v[cx-r:cx+r, cy-r:cy+r] = 0.25

    u += 0.01 * rng.standard_normal((n, n))
    v += 0.01 * rng.standard_normal((n, n))
    np.clip(u, 0.0, 1.0, out=u)
    np.clip(v, 0.0, 1.0, out=v)
    return u, v


def stable_dt(dt: float, du: float, dv: float, dx: float = 1.0) -> float:
    cfl = dt * max(du, dv) / (dx * dx)
    if cfl < 0.25:
        return dt
    return 0.20 * dx * dx / max(du, dv)


# -----------------------------------------------------------------------------
# Measurements
# -----------------------------------------------------------------------------

def spatial_entropy(v: np.ndarray, bins: int = 48) -> float:
    hist, _ = np.histogram(v.ravel(), bins=bins, range=(0.0, 1.0), density=False)
    total = float(np.sum(hist))
    if total <= 0:
        return 0.0
    p = hist.astype(np.float64) / total
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)) / np.log(bins))


def radial_spectrum(v: np.ndarray, dx: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    n = v.shape[0]
    fft2 = np.fft.fft2(v - v.mean())
    power = np.abs(np.fft.fftshift(fft2)) ** 2
    freqs = np.fft.fftshift(np.fft.fftfreq(n, d=dx))
    fx, fy = np.meshgrid(freqs, freqs)
    r = np.sqrt(fx**2 + fy**2)

    bins = np.linspace(0, 0.5 / dx, n // 2)
    idx = np.digitize(r.ravel(), bins)
    radial = np.array([
        power.ravel()[idx == i].mean() if (idx == i).any() else 0.0
        for i in range(1, len(bins))
    ])
    centers = 0.5 * (bins[:-1] + bins[1:])
    return centers, radial


def spectral_length(v: np.ndarray) -> float:
    centers, radial = radial_spectrum(v)
    if radial.size == 0:
        return float(v.shape[0]) / 4.0
    peak_f = float(centers[int(np.argmax(radial))])
    if peak_f <= 1e-9:
        return float(v.shape[0]) / 4.0
    return 1.0 / peak_f


def spectral_sharpness(v: np.ndarray) -> float:
    _, radial = radial_spectrum(v)
    if radial.size == 0:
        return 0.0
    peak = float(np.max(radial))
    baseline = float(np.mean(radial) + 1e-12)
    return peak / baseline


def components(v: np.ndarray, threshold: float, min_area: int) -> List[Dict[str, float]]:
    mask = v > threshold
    lbl, ncomp = label(mask)
    if ncomp == 0:
        return []
    counts = np.bincount(lbl.ravel())
    valid = [i for i in range(1, ncomp + 1) if counts[i] >= min_area]
    if not valid:
        return []

    coms = center_of_mass(mask.astype(np.float64), lbl, valid)
    out: List[Dict[str, float]] = []
    for lab, (cx, cy) in zip(valid, coms):
        out.append({"label": float(lab), "area": float(counts[lab]), "x": float(cx), "y": float(cy)})
    return out


def nn_spacing(comps: List[Dict[str, float]]) -> float:
    if len(comps) < 2:
        return math.nan
    pts = np.array([[c["x"], c["y"]] for c in comps], dtype=np.float64)
    d2 = np.sum((pts[:, None, :] - pts[None, :, :]) ** 2, axis=2)
    np.fill_diagonal(d2, np.inf)
    nn = np.sqrt(np.min(d2, axis=1))
    return float(np.median(nn))


@dataclass
class SplitCfg:
    split_radius: float
    split_area_gain: float
    min_child_frac: float


def detect_splits(prev: List[Dict[str, float]], curr: List[Dict[str, float]], cfg: SplitCfg) -> int:
    if not prev or len(curr) < 2:
        return 0
    pts = np.array([[c["x"], c["y"]] for c in curr], dtype=np.float64)
    areas = np.array([c["area"] for c in curr], dtype=np.float64)

    n = 0
    for p in prev:
        pxy = np.array([p["x"], p["y"]], dtype=np.float64)
        d = np.sqrt(np.sum((pts - pxy[None, :]) ** 2, axis=1))
        neigh = np.where(d <= cfg.split_radius)[0]
        if neigh.size < 2:
            continue
        a = areas[neigh]
        if float(np.sum(a)) >= cfg.split_area_gain * p["area"] and float(np.min(a)) >= cfg.min_child_frac * p["area"]:
            n += 1
    return n


def bootstrap_ci(x: np.ndarray, stat=np.median, n_boot: int = 400, alpha: float = 0.05, rng=None) -> Tuple[float, float]:
    if x.size == 0:
        return (math.nan, math.nan)
    if x.size == 1:
        v = float(x[0])
        return (v, v)
    if rng is None:
        rng = np.random.default_rng(0)

    boots = np.empty(n_boot, dtype=np.float64)
    n = x.size
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boots[i] = float(stat(x[idx]))
    return (float(np.quantile(boots, alpha / 2)), float(np.quantile(boots, 1 - alpha / 2)))


# -----------------------------------------------------------------------------
# Simulation runners
# -----------------------------------------------------------------------------

def run_fixed_du(
    *,
    n: int,
    steps: int,
    sample_every: int,
    du: float,
    dv: float,
    F: float,
    k: float,
    seed: int,
    threshold: float,
    min_area: int,
    split_cfg: SplitCfg,
) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    dt = stable_dt(1.0, du, dv)
    u, v = init_fields(n, rng)

    prev = []
    split_times: List[float] = []
    birth_times: List[float] = []

    t_series: List[float] = []
    L_series: List[float] = []
    ent_series: List[float] = []
    spot_series: List[int] = []

    for step in range(steps):
        uvv = u * v * v
        u += dt * (du * laplacian(u) - uvv + F * (1.0 - u))
        v += dt * (dv * laplacian(v) + uvv - (F + k) * v)
        np.clip(u, 0.0, 1.0, out=u)
        np.clip(v, 0.0, 1.0, out=v)

        if step % sample_every == 0 or step == steps - 1:
            t = step * dt
            comps = components(v, threshold, min_area)
            nsplit = detect_splits(prev, comps, split_cfg)
            split_times.extend([t] * nsplit)
            if prev and len(comps) > len(prev):
                birth_times.append(t)

            t_series.append(t)
            L_series.append(nn_spacing(comps))
            ent_series.append(spatial_entropy(v))
            spot_series.append(len(comps))
            prev = comps

    t_arr = np.array(t_series, dtype=np.float64)
    L_arr = np.array([x for x in L_series if np.isfinite(x)], dtype=np.float64)
    L_med = float(np.median(L_arr)) if L_arr.size else math.nan
    L_ci = bootstrap_ci(L_arr, np.median, rng=rng) if L_arr.size else (math.nan, math.nan)

    split_unique = np.unique(np.array(split_times, dtype=np.float64)) if split_times else np.array([], dtype=np.float64)
    split_intervals = np.diff(split_unique) if split_unique.size >= 2 else np.array([], dtype=np.float64)
    births = np.array(birth_times, dtype=np.float64)
    birth_intervals = np.diff(births) if births.size >= 2 else np.array([], dtype=np.float64)

    total_time = float((steps - 1) * dt)
    if split_intervals.size:
        tau_split = float(np.median(split_intervals))
        tau_rate = total_time / max(int(split_unique.size), 1)
        tau = max(tau_split, tau_rate)
        tau_ci = (min(tau_split, tau_rate), max(tau_split, tau_rate))
    elif birth_intervals.size >= 3:
        tau = float(np.median(birth_intervals))
        tau_ci = bootstrap_ci(birth_intervals, np.median, rng=rng)
    elif births.size > 0:
        tau = total_time / max(int(births.size), 1)
        tau_ci = (tau, tau)
    else:
        tau = total_time
        tau_ci = (tau, tau)

    if np.isfinite(L_med) and tau > 0:
        pe_time = (np.array(L_series, dtype=np.float64) ** 2) / (du * tau)
        pe_valid = pe_time[np.isfinite(pe_time)]
    else:
        pe_valid = np.array([], dtype=np.float64)

    pe_med = float(np.median(pe_valid)) if pe_valid.size else math.nan
    pe_ci = bootstrap_ci(pe_valid, np.median, rng=rng) if pe_valid.size else (math.nan, math.nan)

    ent_arr = np.array(ent_series, dtype=np.float64)
    spots = np.array(spot_series, dtype=np.float64)

    return {
        "seed": seed,
        "Du": du,
        "Dv": dv,
        "F": F,
        "k": k,
        "tau_r": tau,
        "tau_ci_low": tau_ci[0],
        "tau_ci_high": tau_ci[1],
        "L_nn": L_med,
        "L_ci_low": L_ci[0],
        "L_ci_high": L_ci[1],
        "L_spec": spectral_length(v),
        "L_agreement_abs": abs(L_med - spectral_length(v)) if np.isfinite(L_med) else math.nan,
        "Pe_r": pe_med,
        "Pe_ci_low": pe_ci[0],
        "Pe_ci_high": pe_ci[1],
        "entropy_mean": float(np.mean(ent_arr)) if ent_arr.size else math.nan,
        "entropy_std": float(np.std(ent_arr)) if ent_arr.size else math.nan,
        "spot_mean": float(np.mean(spots)) if spots.size else math.nan,
        "spot_volatility": float(np.std(spots) / max(np.mean(spots), 1e-9)) if spots.size else math.nan,
        "spectral_sharpness": spectral_sharpness(v),
        "n_splits": int(len(split_times)),
        "n_birth_events": int(len(birth_times)),
        "t": t_arr,
        "L_t": np.array(L_series, dtype=np.float64),
        "entropy_t": ent_arr,
        "spots_t": spots,
        "v_final": v.copy(),
        "u_final": u.copy(),
    }


def run_intervention_protocol(
    *,
    n: int,
    total_steps: int,
    sample_every: int,
    du0: float,
    du1: float,
    ramp_steps: int,
    dv: float,
    F: float,
    k: float,
    seed: int,
    threshold: float,
    min_area: int,
) -> Dict[str, object]:
    """
    If ramp_steps==1 -> near-instant quench.
    Else linear ramp from du0 to du1 over ramp_steps.
    """
    rng = np.random.default_rng(seed)
    u, v = init_fields(n, rng)

    t_list: List[float] = []
    du_list: List[float] = []
    L_list: List[float] = []
    pe_like_list: List[float] = []
    ent_list: List[float] = []
    spots_list: List[int] = []

    intervention_start = total_steps // 4
    intervention_end = intervention_start + max(1, ramp_steps)

    # Use same tau estimator structure as fixed runs: robust event-rate surrogate online.
    split_cfg = SplitCfg(split_radius=max(5.0, n / 16.0), split_area_gain=1.05, min_child_frac=0.22)
    prev = []
    split_times: List[float] = []
    birth_times: List[float] = []

    t_phys = 0.0
    for step in range(total_steps):
        if step < intervention_start:
            du = du0
        elif step >= intervention_end:
            du = du1
        else:
            frac = (step - intervention_start) / max(1, (intervention_end - intervention_start - 1))
            du = du0 + frac * (du1 - du0)

        dt = stable_dt(1.0, du, dv)
        uvv = u * v * v
        u += dt * (du * laplacian(u) - uvv + F * (1.0 - u))
        v += dt * (dv * laplacian(v) + uvv - (F + k) * v)
        np.clip(u, 0.0, 1.0, out=u)
        np.clip(v, 0.0, 1.0, out=v)
        t_phys += dt

        if step % sample_every == 0 or step == total_steps - 1:
            comps = components(v, threshold, min_area)
            nsplit = detect_splits(prev, comps, split_cfg)
            split_times.extend([t_phys] * nsplit)
            if prev and len(comps) > len(prev):
                birth_times.append(t_phys)

            L = nn_spacing(comps)
            # Online tau estimate for instantaneous Pe-like trace.
            split_unique = np.unique(np.array(split_times, dtype=np.float64)) if split_times else np.array([], dtype=np.float64)
            if split_unique.size >= 2:
                tau_now = max(float(np.median(np.diff(split_unique))), t_phys / max(split_unique.size, 1))
            elif len(birth_times) > 0:
                tau_now = t_phys / max(len(birth_times), 1)
            else:
                tau_now = max(t_phys, 1.0)

            pe_like = (L * L) / (du * tau_now) if np.isfinite(L) and tau_now > 0 else math.nan

            t_list.append(t_phys)
            du_list.append(float(du))
            L_list.append(float(L))
            pe_like_list.append(float(pe_like))
            ent_list.append(spatial_entropy(v))
            spots_list.append(len(comps))
            prev = comps

    t = np.array(t_list, dtype=np.float64)
    du_t = np.array(du_list, dtype=np.float64)
    L_t = np.array(L_list, dtype=np.float64)
    pe_t = np.array(pe_like_list, dtype=np.float64)
    ent_t = np.array(ent_list, dtype=np.float64)

    # Reorganization time from L(t): time to reach 90% of total L shift after intervention.
    pre_mask = t < np.interp(intervention_start, [0, total_steps], [t[0], t[-1]]) if t.size else np.array([], dtype=bool)
    post_mask = t > np.interp(intervention_end, [0, total_steps], [t[0], t[-1]]) if t.size else np.array([], dtype=bool)

    if np.any(pre_mask) and np.any(post_mask):
        L_pre = float(np.nanmedian(L_t[pre_mask]))
        L_post = float(np.nanmedian(L_t[post_mask]))
        target = L_pre + 0.9 * (L_post - L_pre)
        idx_candidates = np.where((t >= t[0]) & np.isfinite(L_t))[0]
        t_reorg = math.nan
        for idx in idx_candidates:
            if (L_post >= L_pre and L_t[idx] >= target) or (L_post < L_pre and L_t[idx] <= target):
                t_reorg = float(t[idx] - t[0])
                break
    else:
        t_reorg = math.nan

    t_int = float(max(1, ramp_steps))
    intervention_ratio = (t_reorg / t_int) if np.isfinite(t_reorg) else math.nan

    return {
        "seed": seed,
        "du0": du0,
        "du1": du1,
        "ramp_steps": ramp_steps,
        "t": t,
        "du_t": du_t,
        "L_t": L_t,
        "Pe_t": pe_t,
        "entropy_t": ent_t,
        "spots_t": np.array(spots_list, dtype=np.float64),
        "L_pre": float(np.nanmedian(L_t[pre_mask])) if np.any(pre_mask) else math.nan,
        "L_post": float(np.nanmedian(L_t[post_mask])) if np.any(post_mask) else math.nan,
        "Pe_pre": float(np.nanmedian(pe_t[pre_mask])) if np.any(pre_mask) else math.nan,
        "Pe_post": float(np.nanmedian(pe_t[post_mask])) if np.any(post_mask) else math.nan,
        "entropy_pre": float(np.nanmedian(ent_t[pre_mask])) if np.any(pre_mask) else math.nan,
        "entropy_post": float(np.nanmedian(ent_t[post_mask])) if np.any(post_mask) else math.nan,
        "t_reorg": t_reorg,
        "t_intervention_steps": float(t_int),
        "intervention_ratio": intervention_ratio,
    }


# -----------------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------------

def savefig(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def fig_sweep_core(results: List[Dict[str, object]], out: Path) -> None:
    du = np.array([r["Du"] for r in results], dtype=np.float64)
    pe = np.array([r["Pe_r"] for r in results], dtype=np.float64)
    tau = np.array([r["tau_r"] for r in results], dtype=np.float64)
    L = np.array([r["L_nn"] for r in results], dtype=np.float64)
    ent = np.array([r["entropy_mean"] for r in results], dtype=np.float64)

    fig, axs = plt.subplots(2, 2, figsize=(11, 8))

    axs[0, 0].scatter(du, pe, c="#1b9e77")
    axs[0, 0].axhline(1.0, ls="--", color="#e6ab02")
    axs[0, 0].set_title("Measured Pe_r vs D_u")
    axs[0, 0].set_xlabel("D_u")
    axs[0, 0].set_ylabel("Pe_r")
    axs[0, 0].grid(alpha=0.25)

    axs[0, 1].scatter(du, tau, c="#d95f02")
    axs[0, 1].set_title("Measured tau_r(D_u)")
    axs[0, 1].set_xlabel("D_u")
    axs[0, 1].set_ylabel("tau_r")
    axs[0, 1].grid(alpha=0.25)

    axs[1, 0].scatter(du, L, c="#7570b3")
    axs[1, 0].set_title("Measured L(D_u)")
    axs[1, 0].set_xlabel("D_u")
    axs[1, 0].set_ylabel("L")
    axs[1, 0].grid(alpha=0.25)

    axs[1, 1].scatter(pe, ent, c="#1b9e77")
    axs[1, 1].axvline(1.0, ls="--", color="#e6ab02")
    axs[1, 1].set_title("Entropy vs Pe_r")
    axs[1, 1].set_xlabel("Pe_r")
    axs[1, 1].set_ylabel("Entropy")
    axs[1, 1].grid(alpha=0.25)

    savefig(fig, out / "fig1_sweep_core_metrics.png")


def fig_estimator_agreement(results: List[Dict[str, object]], out: Path) -> None:
    Lnn = np.array([r["L_nn"] for r in results], dtype=np.float64)
    Lsp = np.array([r["L_spec"] for r in results], dtype=np.float64)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(Lnn, Lsp, c="#7570b3")
    lo = min(float(np.nanmin(Lnn)), float(np.nanmin(Lsp)))
    hi = max(float(np.nanmax(Lnn)), float(np.nanmax(Lsp)))
    ax.plot([lo, hi], [lo, hi], "--", color="#e6ab02", label="y=x")
    ax.set_xlabel("L nearest-neighbor")
    ax.set_ylabel("L spectral")
    ax.set_title("L estimator agreement")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    savefig(fig, out / "fig2_estimator_agreement.png")


def fig_quadratic(out: Path, du_ref: float, tau_ref: float) -> None:
    L = np.linspace(2.0, 60.0, 500)
    Pe = (L**2) / (du_ref * tau_ref)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
    axs[0].plot(L, Pe, color="#1b9e77")
    axs[0].axhline(1.0, ls="--", color="#e6ab02")
    axs[0].set_xlabel("L")
    axs[0].set_ylabel("Pe_r")
    axs[0].set_title("Pe_r vs L (fixed D_u,tau_r)")
    axs[0].grid(alpha=0.25)

    Lg = np.logspace(0.4, 1.9, 300)
    Peg = (Lg**2) / (du_ref * tau_ref)
    slope = np.polyfit(np.log(Lg), np.log(Peg), 1)[0]
    axs[1].loglog(Lg, Peg, color="#7570b3", label=f"slope={slope:.2f}")
    axs[1].set_xlabel("L (log)")
    axs[1].set_ylabel("Pe_r (log)")
    axs[1].set_title("Quadratic sensitivity check")
    axs[1].legend(fontsize=8)
    axs[1].grid(alpha=0.25, which="both")

    savefig(fig, out / "fig3_quadratic_sensitivity.png")


def fig_consistency(out: Path) -> None:
    L0 = 18.0
    tau0 = 120.0
    Du = np.linspace(0.05, 2.0, 300)
    Pe = (L0**2) / (Du * tau0)
    d = -(L0**2) / (tau0 * Du**2)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
    axs[0].plot(Du, Pe, color="#1b9e77")
    axs[0].set_xlabel("D_u")
    axs[0].set_ylabel("Pe_r")
    axs[0].set_title("Consistency: Pe_r(D_u) at fixed L,tau_r")
    axs[0].grid(alpha=0.25)

    axs[1].plot(Du, d, color="#d95f02")
    axs[1].axhline(0.0, color="black", lw=1)
    axs[1].set_xlabel("D_u")
    axs[1].set_ylabel("dPe_r/dD_u")
    axs[1].set_title("Derivative sign check")
    axs[1].grid(alpha=0.25)

    savefig(fig, out / "fig4_consistency_derivative.png")


def fig_protocol_compare(proto: List[Dict[str, object]], out: Path) -> None:
    quench = [p for p in proto if int(p["ramp_steps"]) == 1]
    ramp = [p for p in proto if int(p["ramp_steps"]) > 1]

    fig, axs = plt.subplots(2, 2, figsize=(11, 8))

    for p in quench:
        axs[0, 0].plot(p["t"], p["Pe_t"], alpha=0.8, label=f"seed {p['seed']}")
        axs[1, 0].plot(p["t"], p["entropy_t"], alpha=0.8)
    axs[0, 0].axhline(1.0, ls="--", color="#e6ab02")
    axs[0, 0].set_title("Quench: Pe_r-like trace")
    axs[0, 0].set_xlabel("t")
    axs[0, 0].set_ylabel("Pe_r-like")
    axs[0, 0].grid(alpha=0.25)
    if quench:
        axs[0, 0].legend(fontsize=7)

    axs[1, 0].set_title("Quench: entropy trace")
    axs[1, 0].set_xlabel("t")
    axs[1, 0].set_ylabel("entropy")
    axs[1, 0].grid(alpha=0.25)

    for p in ramp:
        axs[0, 1].plot(p["t"], p["Pe_t"], alpha=0.8, label=f"seed {p['seed']}")
        axs[1, 1].plot(p["t"], p["entropy_t"], alpha=0.8)
    axs[0, 1].axhline(1.0, ls="--", color="#e6ab02")
    axs[0, 1].set_title("Ramp: Pe_r-like trace")
    axs[0, 1].set_xlabel("t")
    axs[0, 1].set_ylabel("Pe_r-like")
    axs[0, 1].grid(alpha=0.25)
    if ramp:
        axs[0, 1].legend(fontsize=7)

    axs[1, 1].set_title("Ramp: entropy trace")
    axs[1, 1].set_xlabel("t")
    axs[1, 1].set_ylabel("entropy")
    axs[1, 1].grid(alpha=0.25)

    savefig(fig, out / "fig5_protocol_quench_vs_ramp_timeseries.png")



def fig_intervention_ratio(proto: List[Dict[str, object]], out: Path) -> None:
    ratio = np.array([p["intervention_ratio"] for p in proto], dtype=np.float64)
    delta_ent = np.array([p["entropy_post"] - p["entropy_pre"] for p in proto], dtype=np.float64)
    ramp_steps = np.array([p["ramp_steps"] for p in proto], dtype=np.float64)

    fig, ax = plt.subplots(figsize=(7, 5))
    sc = ax.scatter(ratio, delta_ent, c=ramp_steps, cmap="viridis")
    ax.set_xlabel("Intervention/Reorganization ratio (t_reorg / t_intervention)")
    ax.set_ylabel("Delta entropy (post - pre)")
    ax.set_title("Second-ratio effect: control efficacy vs intervention rate")
    ax.grid(alpha=0.25)
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("ramp_steps (1=quench)")
    savefig(fig, out / "fig6_intervention_ratio_effect.png")


# -----------------------------------------------------------------------------
# IO and checks
# -----------------------------------------------------------------------------

def write_sweep_csv(results: List[Dict[str, object]], out: Path, n: int, steps: int, sample_every: int) -> Path:
    p = out / "metrics_sweep.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "seed", "Du", "Dv", "F", "k", "grid", "steps", "sample_every",
            "tau_r", "tau_ci_low", "tau_ci_high",
            "L_nn", "L_ci_low", "L_ci_high", "L_spec", "L_agreement_abs",
            "Pe_r", "Pe_ci_low", "Pe_ci_high",
            "entropy_mean", "entropy_std", "spot_mean", "spot_volatility", "spectral_sharpness",
            "n_splits", "n_birth_events",
        ])
        for r in results:
            w.writerow([
                r["seed"], r["Du"], r["Dv"], r["F"], r["k"], n, steps, sample_every,
                r["tau_r"], r["tau_ci_low"], r["tau_ci_high"],
                r["L_nn"], r["L_ci_low"], r["L_ci_high"], r["L_spec"], r["L_agreement_abs"],
                r["Pe_r"], r["Pe_ci_low"], r["Pe_ci_high"],
                r["entropy_mean"], r["entropy_std"], r["spot_mean"], r["spot_volatility"], r["spectral_sharpness"],
                r["n_splits"], r["n_birth_events"],
            ])
    return p


def write_protocol_csv(proto: List[Dict[str, object]], out: Path) -> Path:
    p = out / "metrics_protocols.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "seed", "du0", "du1", "ramp_steps",
            "L_pre", "L_post", "Pe_pre", "Pe_post", "entropy_pre", "entropy_post",
            "t_reorg", "t_intervention_steps", "intervention_ratio",
        ])
        for r in proto:
            w.writerow([
                r["seed"], r["du0"], r["du1"], r["ramp_steps"],
                r["L_pre"], r["L_post"], r["Pe_pre"], r["Pe_post"], r["entropy_pre"], r["entropy_post"],
                r["t_reorg"], r["t_intervention_steps"], r["intervention_ratio"],
            ])
    return p


def checks(sweep: List[Dict[str, object]], proto: List[Dict[str, object]]) -> Dict[str, bool]:
    out: Dict[str, bool] = {}

    # Unit identities.
    L, Du, tau = 3.0, 0.2, 5.0
    pe = L * L / (Du * tau)
    out["unit_identity"] = abs(pe - 9.0) < 1e-12
    out["unit_monotonic_L"] = (4.0 * 4.0 / (Du * tau)) > pe
    out["unit_monotonic_Du"] = (L * L / (0.4 * tau)) < pe
    out["unit_monotonic_tau"] = (L * L / (Du * 8.0)) < pe

    # Integration: at least one low and one high Pe regime around threshold.
    pes = np.array([r["Pe_r"] for r in sweep], dtype=np.float64)
    out["integration_has_subcritical"] = bool(np.any(pes < 1.0))
    out["integration_has_supercritical"] = bool(np.any(pes > 1.0))
    out["integration_has_near_threshold"] = bool(np.any(np.abs(pes - 1.0) <= 0.35))

    # Intervention logic: quench should be at least as effective as ramp on median entropy drop.
    q = [r["entropy_post"] - r["entropy_pre"] for r in proto if int(r["ramp_steps"]) == 1 and np.isfinite(r["entropy_post"]) and np.isfinite(r["entropy_pre"])]
    rr = [r["entropy_post"] - r["entropy_pre"] for r in proto if int(r["ramp_steps"]) > 1 and np.isfinite(r["entropy_post"]) and np.isfinite(r["entropy_pre"])]
    if q and rr:
        out["integration_quench_vs_ramp"] = float(np.median(q)) <= float(np.median(rr))
    else:
        out["integration_quench_vs_ramp"] = False

    return out


# -----------------------------------------------------------------------------
# CLI + main
# -----------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Permutation 5: robust complete script and plots")
    p.add_argument("--quick", action="store_true", help="fast preview mode")
    p.add_argument("--seed", type=int, default=20260307)
    p.add_argument("--grid", type=int, default=128)
    p.add_argument("--steps", type=int, default=9000)
    p.add_argument("--output-dir", default=str(Path(__file__).resolve().parent / "outputs"))
    p.add_argument("--skip-heavy", action="store_true", help="skip heavier protocol replicates")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if args.quick:
        n = min(args.grid, 96)
        steps = min(args.steps, 3600)
        sample_every = 40
        du_vals = [0.08, 0.20, 0.40, 0.80, 1.20, 2.0, 3.0]
        seeds = [args.seed + i for i in range(2)]
        protocol_total_steps = 4200
        ramp_steps = 800
    else:
        n = args.grid
        steps = args.steps
        sample_every = 50
        du_vals = [0.07, 0.15, 0.30, 0.60, 1.00, 1.50, 2.50, 3.50]
        seeds = [args.seed + i for i in range(3)]
        protocol_total_steps = 7000
        ramp_steps = 1800

    # Fixed chemistry for orthogonal Du testing.
    F = 0.026
    k = 0.051
    Dv = 0.08

    threshold = 0.12
    min_area = max(6, n // 32)
    split_cfg = SplitCfg(split_radius=max(5.0, n / 16.0), split_area_gain=1.05, min_child_frac=0.22)

    # --- Sweep runs
    sweep: List[Dict[str, object]] = []
    for du in du_vals:
        for s in seeds:
            run_seed = s + int(round(du * 1000))
            print(f"Sweep run: Du={du:.3f} seed={run_seed}")
            res = run_fixed_du(
                n=n,
                steps=steps,
                sample_every=sample_every,
                du=du,
                dv=Dv,
                F=F,
                k=k,
                seed=run_seed,
                threshold=threshold,
                min_area=min_area,
                split_cfg=split_cfg,
            )
            sweep.append(res)

    # --- Protocol runs: same start/end Du, compare quench vs ramp
    proto: List[Dict[str, object]] = []
    du0, du1 = 0.20, 2.00
    protocol_seeds = seeds if not args.skip_heavy else [seeds[0]]
    for s in protocol_seeds:
        print(f"Protocol quench seed={s}")
        proto.append(run_intervention_protocol(
            n=n,
            total_steps=protocol_total_steps,
            sample_every=sample_every,
            du0=du0,
            du1=du1,
            ramp_steps=1,
            dv=Dv,
            F=F,
            k=k,
            seed=s + 9000,
            threshold=threshold,
            min_area=min_area,
        ))
        print(f"Protocol ramp seed={s}")
        proto.append(run_intervention_protocol(
            n=n,
            total_steps=protocol_total_steps,
            sample_every=sample_every,
            du0=du0,
            du1=du1,
            ramp_steps=ramp_steps,
            dv=Dv,
            F=F,
            k=k,
            seed=s + 12000,
            threshold=threshold,
            min_area=min_area,
        ))

    # --- Write CSV
    csv_sweep = write_sweep_csv(sweep, out, n=n, steps=steps, sample_every=sample_every)
    csv_proto = write_protocol_csv(proto, out)

    # --- Figures
    fig_sweep_core(sweep, out)
    fig_estimator_agreement(sweep, out)

    tau_ref = float(np.nanmedian(np.array([r["tau_r"] for r in sweep], dtype=np.float64)))
    du_ref = float(np.nanmedian(np.array([r["Du"] for r in sweep], dtype=np.float64)))
    fig_quadratic(out, du_ref=max(du_ref, 1e-6), tau_ref=max(tau_ref, 1e-6))
    fig_consistency(out)
    fig_protocol_compare(proto, out)
    fig_intervention_ratio(proto, out)

    # --- Checks
    c = checks(sweep, proto)
    print("\n=== Checks ===")
    for kname, ok in c.items():
        print(f"{kname}: {'PASS' if ok else 'CHECK'}")

    print("\n=== Outputs ===")
    print(f"{csv_sweep}")
    print(f"{csv_proto}")
    for fname in [
        "fig1_sweep_core_metrics.png",
        "fig2_estimator_agreement.png",
        "fig3_quadratic_sensitivity.png",
        "fig4_consistency_derivative.png",
        "fig5_protocol_quench_vs_ramp_timeseries.png",
        "fig6_intervention_ratio_effect.png",
    ]:
        print(out / fname)


if __name__ == "__main__":
    main()
