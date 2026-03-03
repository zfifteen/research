#!/usr/bin/env python3
"""Setup 2 runner: diffusion + 2D Navier-Stokes validation experiments."""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


L_DOMAIN = 2.0 * math.pi


def parse_csv_floats(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


class TeeLogger:
    def __init__(self, path: Path) -> None:
        self._fh = path.open("w", encoding="utf-8")

    def log(self, msg: str) -> None:
        print(msg)
        self._fh.write(msg + "\n")
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()


@dataclass(frozen=True)
class Spectral2D:
    n: int
    kx: np.ndarray
    ky: np.ndarray
    k2: np.ndarray
    dealias: np.ndarray
    kabs: np.ndarray


def make_spectral2d(n: int) -> Spectral2D:
    k1 = np.fft.fftfreq(n, d=1.0 / n)
    kx, ky = np.meshgrid(k1, k1, indexing="xy")
    k2 = kx * kx + ky * ky
    kabs = np.sqrt(k2)
    kcut = n // 3
    dealias = ((np.abs(kx) <= kcut) & (np.abs(ky) <= kcut)).astype(float)
    return Spectral2D(n=n, kx=kx, ky=ky, k2=k2, dealias=dealias, kabs=kabs)


def rms(a: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.real(a) ** 2)))


def rel_l2(a: np.ndarray, b: np.ndarray) -> float:
    d = np.linalg.norm(a - b)
    n = np.linalg.norm(b)
    if n == 0:
        return float("nan")
    return float(d / n)


def nearest_idx(times: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(times - target)))


def k_eta_estimate(n: int, nu: float, u_rms: float) -> int:
    re_eff = max(1.0, (u_rms * L_DOMAIN) / max(nu, 1e-12))
    keta = int(max(4, min(n // 3, 0.20 * (re_eff ** 0.75))))
    return keta


def lowpass_hat(field_hat: np.ndarray, kabs: np.ndarray, k_obs: int) -> np.ndarray:
    out = np.zeros_like(field_hat)
    mask = kabs <= k_obs
    out[mask] = field_hat[mask]
    return out


def mode_skill(recon_hat: np.ndarray, truth_hat: np.ndarray, kabs: np.ndarray, keta: int) -> float:
    mask = (kabs <= keta) & (kabs > 0)
    count = int(np.count_nonzero(mask))
    if count == 0:
        return float("nan")
    tmag = np.abs(truth_hat[mask])
    rmag = np.abs(recon_hat[mask])
    denom = np.maximum(tmag, 1e-12)
    good = np.abs(rmag - tmag) / denom <= 0.2
    return float(np.mean(good))


def info_content(field_hat: np.ndarray, kabs: np.ndarray, keta: int) -> float:
    mask = (kabs <= keta) & (kabs > 0)
    energy = np.abs(field_hat[mask]) ** 2
    return float(np.sum(np.log1p(energy)))


def classify_by_tau(df_cfg: pd.DataFrame) -> str:
    g = df_cfg.sort_values("tau")
    tau = g["tau"].to_numpy()
    ratio = g["growth_ratio"].to_numpy()
    skill = g["skill"].to_numpy()
    z = g["z_tau"].to_numpy()

    cond = (tau >= 2.0) & np.isfinite(ratio) & np.isfinite(skill) & np.isfinite(z)
    if np.count_nonzero(cond) >= 3:
        idx = np.where(cond)[0]
        for i in range(len(idx) - 2):
            j0, j1, j2 = idx[i], idx[i + 1], idx[i + 2]
            if (
                ratio[j0] >= 3.0
                and ratio[j1] >= 3.0
                and ratio[j2] >= 3.0
                and skill[j0] < 0.3
                and skill[j1] < 0.3
                and skill[j2] < 0.3
                and z[j0] >= 1.0
                and z[j1] >= 1.0
                and z[j2] >= 1.0
            ):
                return "Supported"

    condf = (tau >= 3.0) & np.isfinite(ratio)
    if np.count_nonzero(condf) > 0 and np.all(ratio[condf] <= 1.5):
        return "Falsified"
    return "Inconclusive"


def make_initial_field_diffusion(spec: Spectral2D, rng: np.random.Generator) -> np.ndarray:
    coeff = (rng.normal(size=(spec.n, spec.n)) + 1j * rng.normal(size=(spec.n, spec.n)))
    env = np.exp(-(spec.kabs / 10.0) ** 2)
    coeff *= env
    coeff[0, 0] = 0.0
    field = np.fft.ifft2(coeff).real
    return field / max(rms(field), 1e-12)


def evolve_diffusion(u0: np.ndarray, nu: float, t_end: float, dt: float, spec: Spectral2D) -> tuple[np.ndarray, np.ndarray]:
    steps = int(math.ceil(t_end / dt))
    times = np.arange(steps + 1, dtype=float) * dt
    hist = np.empty((steps + 1, spec.n, spec.n), dtype=float)
    hist[0] = u0
    u_hat = np.fft.fft2(u0)
    fac = np.exp(-nu * spec.k2 * dt)
    for i in range(1, steps + 1):
        u_hat = u_hat * fac
        hist[i] = np.fft.ifft2(u_hat).real
    return times, hist


def run_exp1(args: argparse.Namespace, out_dir: Path, logger: TeeLogger, seed_seq: np.random.SeedSequence) -> tuple[pd.DataFrame, dict]:
    spec = make_spectral2d(args.e1_N)
    nu_list = parse_csv_floats(args.e1_nu_list)
    noise_list = parse_csv_floats(args.e1_noise_rel_list)
    taus = np.linspace(args.e1_tau_min, args.e1_tau_max, args.e1_tau_points)
    k_obs = args.e1_N // args.e2_obs_kfrac

    rows: list[dict] = []
    snap_data = {}
    child = iter(seed_seq.spawn(len(nu_list) * len(noise_list) + 1))
    init_rng = np.random.default_rng(next(child))
    u0 = make_initial_field_diffusion(spec, init_rng)
    u_rms0 = rms(u0)
    t_int = L_DOMAIN / max(u_rms0, 1e-12)
    dt = args.dt if args.dt is not None else 0.005
    t_obs = (args.e1_tau_max + 0.5) * t_int

    for nu in nu_list:
        times, hist = evolve_diffusion(u0, nu=nu, t_end=t_obs, dt=dt, spec=spec)
        idx_obs = nearest_idx(times, t_obs)
        u_obs_truth = hist[idx_obs]
        u_obs_truth_hat = np.fft.fft2(u_obs_truth)
        keta = k_eta_estimate(spec.n, nu, u_rms0)
        info_obs = info_content(u_obs_truth_hat, spec.kabs, keta)
        logger.log(f"[exp1] nu={nu:g}, N={spec.n}, dt={dt:g}, t_obs={times[idx_obs]:.4f}")

        for noise_rel in noise_list:
            rng = np.random.default_rng(next(child))
            u_obs_lp = np.fft.ifft2(lowpass_hat(u_obs_truth_hat, spec.kabs, k_obs)).real
            noisy = u_obs_lp + noise_rel * rms(u_obs_truth) * rng.normal(size=u_obs_lp.shape)
            noisy_hat = np.fft.fft2(noisy)

            for tau in taus:
                t_past = times[idx_obs] - tau * t_int
                if t_past < 0.0:
                    continue
                idx_past = nearest_idx(times, t_past)
                tau_eff = (times[idx_obs] - times[idx_past]) / t_int
                u_past_truth = hist[idx_past]
                u_fwd = np.fft.ifft2(np.fft.fft2(u_past_truth) * np.exp(-nu * spec.k2 * (times[idx_obs] - times[idx_past]))).real
                u_bwd = np.fft.ifft2(noisy_hat * np.exp(+nu * spec.k2 * (times[idx_obs] - times[idx_past]))).real

                rmse_fwd = rel_l2(u_fwd, u_obs_truth)
                rmse_bwd = rel_l2(u_bwd, u_past_truth)
                growth = rmse_bwd / max(rmse_fwd, 1e-12)

                u_past_hat = np.fft.fft2(u_past_truth)
                u_bwd_hat = np.fft.fft2(u_bwd)
                skill = mode_skill(u_bwd_hat, u_past_hat, spec.kabs, keta)
                info_past = info_content(u_past_hat, spec.kabs, keta)
                loss_rate = max(0.0, (info_past - info_obs) / max(tau_eff, 1e-12))
                cap = int(np.count_nonzero((spec.kabs <= keta) & (spec.kabs > 0)))
                z_tau = (1.0 - skill) * (loss_rate * tau_eff) / max(cap, 1)

                rows.append(
                    {
                        "exp": "exp1",
                        "nu": nu,
                        "noise_rel": noise_rel,
                        "tau": tau_eff,
                        "rmse_fwd": rmse_fwd,
                        "rmse_bwd": rmse_bwd,
                        "growth_ratio": growth,
                        "skill": skill,
                        "loss_rate": loss_rate,
                        "capacity": cap,
                        "z_tau": z_tau,
                        "verdict": "",
                    }
                )

            if args.save_snapshots:
                snap_data[f"nu_{nu:g}_noise_{noise_rel:g}_truth_obs"] = u_obs_truth
                snap_data[f"nu_{nu:g}_noise_{noise_rel:g}_obs_noisy"] = noisy

    df = pd.DataFrame(rows).sort_values(["nu", "noise_rel", "tau"])
    for (nu, noise_rel), g in df.groupby(["nu", "noise_rel"]):
        verdict = classify_by_tau(g)
        df.loc[(df["nu"] == nu) & (df["noise_rel"] == noise_rel), "verdict"] = verdict

    if args.save_npz and len(snap_data) > 0:
        np.savez_compressed(out_dir / "results_exp1.npz", **snap_data)

    cfg_summary = {}
    for (nu, noise_rel), g in df.groupby(["nu", "noise_rel"]):
        cfg_summary[f"nu={nu:g}|noise={noise_rel:g}"] = {
            "verdict": str(g["verdict"].iloc[0]),
            "max_growth_ratio": float(np.nanmax(g["growth_ratio"])),
            "min_skill": float(np.nanmin(g["skill"])),
            "max_z_tau": float(np.nanmax(g["z_tau"])),
        }
    return df, cfg_summary


def make_initial_vorticity_ns(spec: Spectral2D, rng: np.random.Generator, k0: float) -> np.ndarray:
    coeff = (rng.normal(size=(spec.n, spec.n)) + 1j * rng.normal(size=(spec.n, spec.n)))
    kk = np.maximum(spec.kabs, 1.0)
    env = (kk ** -2.0) * np.exp(-(kk / k0) ** 2)
    coeff *= env
    coeff[0, 0] = 0.0
    omega = np.fft.ifft2(coeff).real
    return omega / max(rms(omega), 1e-12)


def ns_nonlinear_hat(omega_hat: np.ndarray, spec: Spectral2D) -> np.ndarray:
    inv_lap = np.zeros_like(spec.k2, dtype=float)
    mask = spec.k2 > 0
    inv_lap[mask] = 1.0 / spec.k2[mask]
    psi_hat = -omega_hat * inv_lap
    u_hat = 1j * spec.ky * psi_hat
    v_hat = -1j * spec.kx * psi_hat
    dwdx_hat = 1j * spec.kx * omega_hat
    dwdy_hat = 1j * spec.ky * omega_hat
    u = np.fft.ifft2(u_hat).real
    v = np.fft.ifft2(v_hat).real
    dwdx = np.fft.ifft2(dwdx_hat).real
    dwdy = np.fft.ifft2(dwdy_hat).real
    adv = u * dwdx + v * dwdy
    return -np.fft.fft2(adv) * spec.dealias


def ns_ifrk4_step(omega_hat: np.ndarray, nu: float, dt: float, spec: Spectral2D) -> np.ndarray:
    lk = -nu * spec.k2
    q0 = omega_hat

    def f(s: float, q: np.ndarray) -> np.ndarray:
        exp_ls = np.exp(lk * s)
        wh = exp_ls * q
        nh = ns_nonlinear_hat(wh, spec)
        return nh / exp_ls

    k1 = f(0.0, q0)
    k2 = f(0.5 * dt, q0 + 0.5 * dt * k1)
    k3 = f(0.5 * dt, q0 + 0.5 * dt * k2)
    k4 = f(dt, q0 + dt * k3)
    qn = q0 + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    wn = np.exp(lk * dt) * qn
    return wn * spec.dealias


def simulate_ns(omega0: np.ndarray, nu: float, t_end: float, dt: float, spec: Spectral2D) -> tuple[np.ndarray, np.ndarray]:
    steps = int(math.ceil(t_end / dt))
    times = np.arange(steps + 1, dtype=float) * dt
    hist = np.empty((steps + 1, spec.n, spec.n), dtype=float)
    hist[0] = omega0
    w_hat = np.fft.fft2(omega0)
    for i in range(1, steps + 1):
        w_hat = ns_ifrk4_step(w_hat, nu=nu, dt=dt, spec=spec)
        hist[i] = np.fft.ifft2(w_hat).real
    return times, hist


def evolve_ns(omega: np.ndarray, nu: float, duration: float, dt: float, spec: Spectral2D) -> np.ndarray:
    steps = int(max(0, round(duration / dt)))
    if steps == 0:
        return omega.copy()
    w_hat = np.fft.fft2(omega)
    for _ in range(steps):
        w_hat = ns_ifrk4_step(w_hat, nu=nu, dt=dt, spec=spec)
    return np.fft.ifft2(w_hat).real


def velocity_rms_from_omega(omega: np.ndarray, spec: Spectral2D) -> float:
    w_hat = np.fft.fft2(omega)
    inv_lap = np.zeros_like(spec.k2, dtype=float)
    mask = spec.k2 > 0
    inv_lap[mask] = 1.0 / spec.k2[mask]
    psi_hat = -w_hat * inv_lap
    u = np.fft.ifft2(1j * spec.ky * psi_hat).real
    v = np.fft.ifft2(-1j * spec.kx * psi_hat).real
    return float(np.sqrt(np.mean(u * u + v * v)))


def run_exp2(args: argparse.Namespace, out_dir: Path, logger: TeeLogger, seed_seq: np.random.SeedSequence) -> tuple[pd.DataFrame, dict, dict]:
    spec = make_spectral2d(args.e2_N)
    nu_list = parse_csv_floats(args.e2_nu_list)
    noise_list = parse_csv_floats(args.e2_noise_rel_list)
    taus = np.linspace(args.e2_tau_min, args.e2_tau_max, args.e2_tau_points)
    k_obs = args.e2_N // args.e2_obs_kfrac
    rows: list[dict] = []
    snapshots: dict[str, np.ndarray] = {}

    child = iter(seed_seq.spawn(len(nu_list) * len(noise_list) + 1))
    rng_init = np.random.default_rng(next(child))
    omega0 = make_initial_vorticity_ns(spec, rng_init, args.e2_k0)
    uref = max(velocity_rms_from_omega(omega0, spec), 1e-8)
    t_int = L_DOMAIN / uref
    dt = args.dt if args.dt is not None else min(0.01, 0.25 * (L_DOMAIN / args.e2_N) / uref)
    t_obs = (args.e2_tau_max + 0.6) * t_int

    for nu in nu_list:
        times, hist = simulate_ns(omega0, nu=nu, t_end=t_obs, dt=dt, spec=spec)
        idx_obs = nearest_idx(times, t_obs)
        w_obs_truth = hist[idx_obs]
        w_obs_hat = np.fft.fft2(w_obs_truth)
        obs_clean = lowpass_hat(w_obs_hat, spec.kabs, k_obs)
        keta = k_eta_estimate(spec.n, nu, uref)
        info_obs = info_content(w_obs_hat, spec.kabs, keta)
        logger.log(f"[exp2] nu={nu:g}, N={spec.n}, dt={dt:g}, t_obs={times[idx_obs]:.4f}")

        for noise_rel in noise_list:
            rng = np.random.default_rng(next(child))
            obs_scale = np.sqrt(np.mean(np.abs(obs_clean[spec.kabs <= k_obs]) ** 2))
            sigma = noise_rel * max(obs_scale, 1e-12) / math.sqrt(2.0)
            noise = rng.normal(0.0, sigma, size=obs_clean.shape) + 1j * rng.normal(0.0, sigma, size=obs_clean.shape)
            obs_noisy = np.zeros_like(obs_clean)
            mask_obs = spec.kabs <= k_obs
            obs_noisy[mask_obs] = obs_clean[mask_obs] + noise[mask_obs]
            w_present = np.fft.ifft2(obs_noisy).real

            for tau in taus:
                t_past = times[idx_obs] - tau * t_int
                if t_past < 0.0:
                    continue
                idx_past = nearest_idx(times, t_past)
                dur = times[idx_obs] - times[idx_past]
                tau_eff = dur / t_int
                w_past_truth = hist[idx_past]

                w_fwd = evolve_ns(w_past_truth, nu=nu, duration=dur, dt=dt, spec=spec)
                rmse_fwd = rel_l2(w_fwd, w_obs_truth)

                status = "ok"
                rmse_bwd = float("nan")
                skill = float("nan")
                loss_rate = float("nan")
                z_tau = float("nan")
                try:
                    w_bwd = evolve_ns(w_present, nu=-nu, duration=dur, dt=dt, spec=spec)
                    if not np.isfinite(w_bwd).all():
                        raise FloatingPointError("non-finite backward state")
                    rmse_bwd = rel_l2(w_bwd, w_past_truth)
                    w_bwd_hat = np.fft.fft2(w_bwd)
                    w_past_hat = np.fft.fft2(w_past_truth)
                    skill = mode_skill(w_bwd_hat, w_past_hat, spec.kabs, keta)
                    info_past = info_content(w_past_hat, spec.kabs, keta)
                    loss_rate = max(0.0, (info_past - info_obs) / max(tau_eff, 1e-12))
                    cap = int(np.count_nonzero((spec.kabs <= keta) & (spec.kabs > 0)))
                    z_tau = (1.0 - skill) * (loss_rate * tau_eff) / max(cap, 1)
                except (FloatingPointError, OverflowError, ValueError):
                    status = "diverged"
                    cap = int(np.count_nonzero((spec.kabs <= keta) & (spec.kabs > 0)))

                growth = rmse_bwd / max(rmse_fwd, 1e-12) if np.isfinite(rmse_bwd) else float("nan")
                rows.append(
                    {
                        "exp": "exp2",
                        "nu": nu,
                        "noise_rel": noise_rel,
                        "obs_kfrac": args.e2_obs_kfrac,
                        "tau": tau_eff,
                        "rmse_fwd": rmse_fwd,
                        "rmse_bwd": rmse_bwd,
                        "growth_ratio": growth,
                        "skill": skill,
                        "loss_rate": loss_rate,
                        "capacity": cap,
                        "z_tau": z_tau,
                        "status": status,
                        "verdict": "",
                    }
                )

            if args.save_snapshots:
                key = f"nu={nu:g}|noise={noise_rel:g}"
                tau_pick = [taus[0], taus[len(taus) // 2], taus[-1]]
                for i, t in enumerate(tau_pick, start=1):
                    idx_p = nearest_idx(times, times[idx_obs] - t * t_int)
                    snapshots[f"{key}|truth_past_{i}"] = hist[idx_p]
                snapshots[f"{key}|present_truth"] = w_obs_truth
                snapshots[f"{key}|present_obs"] = w_present

    df = pd.DataFrame(rows).sort_values(["nu", "noise_rel", "tau"])
    for (nu, noise_rel), g in df.groupby(["nu", "noise_rel"]):
        verdict = classify_by_tau(g[g["status"] == "ok"])
        df.loc[(df["nu"] == nu) & (df["noise_rel"] == noise_rel), "verdict"] = verdict

    if args.save_npz and len(snapshots) > 0:
        np.savez_compressed(out_dir / "results_exp2.npz", **snapshots)

    cfg_summary = {}
    for (nu, noise_rel), g in df.groupby(["nu", "noise_rel"]):
        cfg_summary[f"nu={nu:g}|noise={noise_rel:g}"] = {
            "verdict": str(g["verdict"].iloc[0]),
            "max_growth_ratio": float(np.nanmax(g["growth_ratio"])),
            "min_skill": float(np.nanmin(g["skill"])),
            "max_z_tau": float(np.nanmax(g["z_tau"])),
            "diverged_rows": int(np.count_nonzero(g["status"] == "diverged")),
        }
    return df, cfg_summary, snapshots


def plot_error_growth(df1: pd.DataFrame | None, df2: pd.DataFrame | None, out_path: Path) -> None:
    noises = sorted(
        {
            *(df1["noise_rel"].unique().tolist() if df1 is not None and len(df1) else []),
            *(df2["noise_rel"].unique().tolist() if df2 is not None and len(df2) else []),
        }
    )
    if not noises:
        return
    fig, axes = plt.subplots(2, len(noises), figsize=(5 * len(noises), 8), squeeze=False)
    for c, noise in enumerate(noises):
        for r, (df, title) in enumerate([(df1, "Exp1"), (df2, "Exp2")]):
            ax = axes[r, c]
            ax.set_title(f"{title} noise={noise:g}")
            if df is None or len(df) == 0:
                continue
            d = df[df["noise_rel"] == noise]
            for nu, g in d.groupby("nu"):
                g = g.sort_values("tau")
                ax.plot(g["tau"], g["rmse_fwd"], "-", label=f"nu={nu:g} fwd")
                ax.plot(g["tau"], g["rmse_bwd"], "--", label=f"nu={nu:g} bwd")
            ax.set_xlabel("tau")
            ax.set_ylabel("RMSE")
            ax.grid(alpha=0.3)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_z_tau(df1: pd.DataFrame | None, df2: pd.DataFrame | None, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, (df, title) in zip(axes, [(df1, "Exp1"), (df2, "Exp2")]):
        ax.set_title(f"{title}: z(tau) vs Re proxy")
        if df is not None and len(df):
            for (nu, noise), g in df.groupby(["nu", "noise_rel"]):
                g = g.sort_values("tau")
                ax.plot(g["tau"], g["z_tau"], marker="o", linewidth=1.2, markersize=3, label=f"1/nu={1/nu:.0f}, noise={noise:g}")
        ax.set_xlabel("tau")
        ax.set_ylabel("z(tau)")
        ax.grid(alpha=0.3)
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_vorticity_snapshots(snapshot_file: Path, out_path: Path) -> None:
    if not snapshot_file.exists():
        return
    data = np.load(snapshot_file)
    keys = sorted([k for k in data.files if "truth_past_" in k])
    if not keys:
        return
    keys = keys[:3]
    fig, axes = plt.subplots(len(keys), 2, figsize=(8, 3 * len(keys)))
    if len(keys) == 1:
        axes = np.array([axes])
    for i, k in enumerate(keys):
        base = k.split("|truth_past_")[0]
        truth = data[k]
        present_obs = data[f"{base}|present_obs"]
        axes[i, 0].imshow(truth, cmap="RdBu_r", origin="lower")
        axes[i, 0].set_title(f"{base} truth past")
        axes[i, 1].imshow(present_obs, cmap="RdBu_r", origin="lower")
        axes[i, 1].set_title(f"{base} observed present")
        axes[i, 0].axis("off")
        axes[i, 1].axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def determine_runtime_mode(args: argparse.Namespace) -> str:
    if args.e1_N <= 128 or args.e2_N <= 128 or args.e2_tau_points <= 12:
        return "fallback"
    return "full"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Setup 2 experiments.")
    parser.add_argument("--outdir", default="results")
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--exp", choices=["all", "exp1", "exp2"], default="all")
    parser.add_argument("--dt", type=float, default=None)
    parser.add_argument("--e1-N", type=int, default=256)
    parser.add_argument("--e1-nu-list", default="1e-3,5e-4,2e-4")
    parser.add_argument("--e1-noise-rel-list", default="0.01,0.02,0.05")
    parser.add_argument("--e1-tau-min", type=float, default=0.5)
    parser.add_argument("--e1-tau-max", type=float, default=5.0)
    parser.add_argument("--e1-tau-points", type=int, default=20)
    parser.add_argument("--e2-N", type=int, default=256)
    parser.add_argument("--e2-nu-list", default="1e-3,5e-4,2e-4,1e-4")
    parser.add_argument("--e2-k0", type=float, default=8.0)
    parser.add_argument("--e2-tau-min", type=float, default=0.5)
    parser.add_argument("--e2-tau-max", type=float, default=3.5)
    parser.add_argument("--e2-tau-points", type=int, default=16)
    parser.add_argument("--e2-obs-kfrac", type=int, default=16)
    parser.add_argument("--e2-noise-rel-list", default="0.01,0.02,0.05")
    parser.add_argument("--save-snapshots", type=lambda x: str(x).lower() == "true", default=True)
    parser.add_argument("--save-npz", type=lambda x: str(x).lower() == "true", default=True)
    args = parser.parse_args()

    started = time.time()
    out_root = Path(args.outdir).expanduser().resolve()
    out_dir = out_root / datetime.now().strftime("%Y%m%d_%H%M%S")
    ensure_dir(out_dir)
    logger = TeeLogger(out_dir / "run.log")
    logger.log(f"Output directory: {out_dir}")
    logger.log(f"Arguments: {vars(args)}")
    runtime_mode = determine_runtime_mode(args)
    logger.log(f"Runtime mode: {runtime_mode}")

    ss = np.random.SeedSequence(args.seed)
    df1 = None
    df2 = None
    exp1_summary = {}
    exp2_summary = {}
    if args.exp in ("all", "exp1"):
        df1, exp1_summary = run_exp1(args, out_dir, logger, ss.spawn(1)[0])
        df1.to_csv(out_dir / "metrics_exp1.csv", index=False)
        logger.log(f"Saved: {out_dir / 'metrics_exp1.csv'}")
    if args.exp in ("all", "exp2"):
        df2, exp2_summary, _ = run_exp2(args, out_dir, logger, ss.spawn(1)[0])
        df2.to_csv(out_dir / "metrics_exp2.csv", index=False)
        logger.log(f"Saved: {out_dir / 'metrics_exp2.csv'}")

    plot_error_growth(df1, df2, out_dir / "error_growth_forward_vs_backward.png")
    plot_z_tau(df1, df2, out_dir / "z_tau_vs_Re.png")
    if args.save_npz and (out_dir / "results_exp2.npz").exists():
        plot_vorticity_snapshots(out_dir / "results_exp2.npz", out_dir / "vorticity_truth_vs_recon_snapshots.png")

    def summarize_global(*summaries: dict) -> str:
        verdicts = []
        for s in summaries:
            verdicts.extend([v["verdict"] for v in s.values()])
        if any(v == "Supported" for v in verdicts):
            return "Supported"
        if verdicts and all(v == "Falsified" for v in verdicts):
            return "Falsified"
        return "Inconclusive"

    summary = {
        "run_config": vars(args),
        "runtime_mode": runtime_mode,
        "runtime_seconds": time.time() - started,
        "exp1_summary": exp1_summary,
        "exp2_summary": exp2_summary,
        "global_outcome": summarize_global(exp1_summary, exp2_summary),
    }
    with (out_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    logger.log(f"Saved: {out_dir / 'summary.json'}")
    logger.close()


if __name__ == "__main__":
    main()
