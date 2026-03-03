#!/usr/bin/env python3
"""Setup 1 validation/falsification experiment for the Light-Cone Trap hypothesis.

1D viscous Burgers (periodic), low-pass noisy observations, and comparison of:
- forward forecast error
- backward reconstruction error and ensemble spread
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


L_DOMAIN = 2.0 * math.pi


@dataclass(frozen=True)
class SolverConfig:
    n: int
    nu: float
    dt: float
    k: np.ndarray
    k2: np.ndarray
    dealias_mask: np.ndarray


def parse_csv_floats(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def parse_csv_ints(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def make_wavenumbers(n: int) -> np.ndarray:
    # Integer Fourier modes for periodic domain x in [0, 2*pi).
    return np.fft.fftfreq(n, d=1.0 / n)


def make_initial_condition(n: int, seed: int, kmax: int = 8) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, L_DOMAIN, n, endpoint=False)
    u0 = np.zeros_like(x)
    for kmode in range(1, kmax + 1):
        phase = rng.uniform(0.0, 2.0 * math.pi)
        amp = 1.0 / kmode
        u0 += amp * np.sin(kmode * x + phase)
    # Normalize to O(1) RMS to keep ranges consistent across seeds.
    u0 /= np.sqrt(np.mean(u0**2))
    return u0


def make_solver_config(n: int, nu: float, dt: float) -> SolverConfig:
    k = make_wavenumbers(n)
    k2 = k * k
    k_cut = n // 3
    dealias_mask = (np.abs(k) <= k_cut).astype(float)
    return SolverConfig(n=n, nu=nu, dt=dt, k=k, k2=k2, dealias_mask=dealias_mask)


def nonlinear_hat(uhat: np.ndarray, cfg: SolverConfig) -> np.ndarray:
    # Burgers nonlinearity: -u u_x = -0.5 d_x(u^2)
    u = np.fft.ifft(uhat, axis=-1).real
    u2_hat = np.fft.fft(u * u, axis=-1)
    return -0.5j * cfg.k * (u2_hat * cfg.dealias_mask)


def ifrk4_step_u_hat(uhat: np.ndarray, cfg: SolverConfig) -> np.ndarray:
    dt = cfg.dt
    lk = -cfg.nu * cfg.k2

    # Local integrating-factor RK4 over one step to avoid large exp(lk * t).
    # q(s) = exp(-L s) u(t_n + s), s in [0, dt], q(0)=u_n.
    q0 = uhat

    def f(s: float, q_now: np.ndarray) -> np.ndarray:
        exp_ls = np.exp(lk * s)
        uh = exp_ls * q_now
        nh = nonlinear_hat(uh, cfg)
        return nh / exp_ls

    k1 = f(0.0, q0)
    k2 = f(0.5 * dt, q0 + 0.5 * dt * k1)
    k3 = f(0.5 * dt, q0 + 0.5 * dt * k2)
    k4 = f(dt, q0 + dt * k3)
    q_next = q0 + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    uhat_next = np.exp(lk * dt) * q_next
    # Keep de-aliased region clean.
    return uhat_next * cfg.dealias_mask


def simulate_from_u0(u0: np.ndarray, t_end: float, cfg: SolverConfig) -> tuple[np.ndarray, np.ndarray]:
    n_steps = int(math.ceil(t_end / cfg.dt))
    times = np.arange(n_steps + 1, dtype=float) * cfg.dt
    u_hist = np.empty((n_steps + 1, cfg.n), dtype=float)
    u_hist[0] = u0
    uhat = np.fft.fft(u0)
    for i in range(1, n_steps + 1):
        uhat = ifrk4_step_u_hat(uhat, cfg)
        u_hist[i] = np.fft.ifft(uhat).real
    return times, u_hist


def evolve_batch(u_batch: np.ndarray, duration: float, cfg: SolverConfig) -> np.ndarray:
    n_steps = max(0, int(round(duration / cfg.dt)))
    if n_steps == 0:
        return u_batch.copy()

    uhat = np.fft.fft(u_batch, axis=-1)
    for _ in range(n_steps):
        uhat = ifrk4_step_u_hat(uhat, cfg)
    return np.fft.ifft(uhat, axis=-1).real


def nearest_idx(times: np.ndarray, target_t: float) -> int:
    idx = int(np.argmin(np.abs(times - target_t)))
    return idx


def lowpass_obs_mask(k: np.ndarray, k_obs: int) -> np.ndarray:
    return np.abs(k) <= k_obs


def apply_observation(uhat: np.ndarray, obs_mask: np.ndarray) -> np.ndarray:
    return uhat[obs_mask]


def add_complex_gaussian_noise(vec: np.ndarray, eps: float, rng: np.random.Generator) -> np.ndarray:
    if eps <= 0.0:
        return vec.copy()
    sigma = eps / math.sqrt(2.0)
    noise = rng.normal(0.0, sigma, size=vec.shape) + 1j * rng.normal(0.0, sigma, size=vec.shape)
    return vec + noise


def rmse_rel(pred: np.ndarray, truth: np.ndarray) -> float:
    denom = np.linalg.norm(truth)
    if denom == 0.0:
        return float("nan")
    return float(np.linalg.norm(pred - truth) / denom)


def make_bandlimited_perturbations(
    rng: np.random.Generator,
    k: np.ndarray,
    shape: tuple[int, int],
    max_mode: int,
    scale: float,
) -> np.ndarray:
    k_mask = (np.abs(k) > 0) & (np.abs(k) <= max_mode)
    coeff = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    coeff *= k_mask[None, :]
    pert = np.fft.ifft(coeff, axis=-1).real
    std = np.std(pert, axis=1, keepdims=True)
    std[std == 0.0] = 1.0
    pert = pert / std
    return scale * pert


def evaluate_candidates(
    candidates: np.ndarray,
    duration: float,
    cfg: SolverConfig,
    y_obs: np.ndarray,
    obs_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    evolved = evolve_batch(candidates, duration, cfg)
    evolved_hat = np.fft.fft(evolved, axis=-1)
    y_pred = evolved_hat[:, obs_mask]
    misfit = np.linalg.norm(y_pred - y_obs[None, :], axis=1)
    return evolved, misfit


def fit_slope(tau: np.ndarray, values: np.ndarray, lo: float = 1.0, hi: float = 3.0) -> float | None:
    mask = (tau >= lo) & (tau <= hi) & np.isfinite(values)
    if mask.sum() < 2:
        return None
    coeff = np.polyfit(tau[mask], values[mask], deg=1)
    return float(coeff[0])


def classify_config(
    tau: np.ndarray,
    rmse_fwd: np.ndarray,
    rmse_bwd: np.ndarray,
    spread: np.ndarray,
    u_rms: float,
) -> tuple[float | None, str]:
    ratio = np.full_like(rmse_fwd, np.nan, dtype=float)
    valid = np.isfinite(rmse_fwd) & np.isfinite(rmse_bwd) & (rmse_fwd > 0.0)
    ratio[valid] = rmse_bwd[valid] / rmse_fwd[valid]
    spread_rel = spread / u_rms

    tau_star = None
    for i in range(max(0, len(tau) - 2)):
        if (
            np.isfinite(ratio[i])
            and np.isfinite(ratio[i + 1])
            and np.isfinite(ratio[i + 2])
            and np.isfinite(spread_rel[i])
            and np.isfinite(spread_rel[i + 1])
            and np.isfinite(spread_rel[i + 2])
            and ratio[i] >= 3.0
            and ratio[i + 1] >= 3.0
            and ratio[i + 2] >= 3.0
            and spread_rel[i] >= 0.10
            and spread_rel[i + 1] >= 0.10
            and spread_rel[i + 2] >= 0.10
        ):
            tau_star = float(tau[i])
            break

    if tau_star is not None:
        return tau_star, "Supported"

    far = tau >= 2.0
    far_valid = far & np.isfinite(ratio) & np.isfinite(spread_rel)
    if far_valid.any():
        if np.all(ratio[far_valid] < 2.0) and np.all(spread_rel[far_valid] < 0.05):
            return None, "Falsified"
    return None, "Inconclusive"


def write_summary(summary_path: Path, summary_obj: dict) -> None:
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary_obj, f, indent=2, sort_keys=True)


def plot_metric(df: pd.DataFrame, y_col: str, title: str, ylabel: str, out_path: Path) -> None:
    plt.figure(figsize=(9, 5))
    grouped = df.groupby(["nu", "eps_rel", "kobs_frac"], dropna=False)
    for (nu, eps_rel, kobs_frac), g in grouped:
        g = g.sort_values("tau")
        label = f"nu={nu:g}, eps={eps_rel:g}, k=N/{int(kobs_frac)}"
        plt.plot(g["tau"], g[y_col], marker="o", linewidth=1.5, markersize=4, label=label)
    plt.xlabel("tau (eddy turnovers)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best", fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


class TeeLogger:
    def __init__(self, log_path: Path) -> None:
        self.log_file = log_path.open("w", encoding="utf-8")

    def log(self, msg: str) -> None:
        print(msg)
        self.log_file.write(msg + "\n")
        self.log_file.flush()

    def close(self) -> None:
        self.log_file.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Setup 1 validation/falsification experiment.")
    parser.add_argument("--outdir", default="results", help="Output directory root.")
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--N", type=int, default=1024)
    parser.add_argument("--nu-list", default="1e-2,2e-3")
    parser.add_argument("--kobs-frac-list", default="16")
    parser.add_argument("--eps-rel-list", default="1e-3")
    parser.add_argument("--tau-min", type=float, default=0.25)
    parser.add_argument("--tau-max", type=float, default=3.0)
    parser.add_argument("--tau-points", type=int, default=12)
    parser.add_argument("--K", type=int, default=64)
    parser.add_argument("--dt", type=float, default=None, help="Fixed dt. If omitted, auto from CFL cap.")
    args = parser.parse_args()

    nu_list = parse_csv_floats(args.nu_list)
    kobs_frac_list = parse_csv_ints(args.kobs_frac_list)
    eps_rel_list = parse_csv_floats(args.eps_rel_list)
    tau_grid = np.linspace(args.tau_min, args.tau_max, args.tau_points)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = Path(args.outdir).expanduser().resolve()
    out_dir = out_root / ts
    ensure_dir(out_dir)
    logger = TeeLogger(out_dir / "run.log")

    logger.log(f"Output directory: {out_dir}")
    logger.log(f"Seed: {args.seed}, N: {args.N}, K: {args.K}")
    logger.log(f"nu_list={nu_list}, kobs_frac_list={kobs_frac_list}, eps_rel_list={eps_rel_list}")

    rows: list[dict] = []
    summary: dict[str, dict] = {}
    u0 = make_initial_condition(args.N, args.seed)
    u_rms = float(np.sqrt(np.mean(u0**2)))
    t_eddy = L_DOMAIN / max(u_rms, 1e-12)
    logger.log(f"Computed U_rms={u_rms:.6f}, T_eddy={t_eddy:.6f}")

    # Build reproducible config-specific seeds.
    cfg_seeds = {}
    seed_seq = np.random.SeedSequence(args.seed)
    total_cfgs = len(nu_list) * len(kobs_frac_list) * len(eps_rel_list)
    child_seqs = seed_seq.spawn(total_cfgs)
    idx = 0
    for nu in nu_list:
        for kf in kobs_frac_list:
            for eps_rel in eps_rel_list:
                cfg_seeds[(nu, kf, eps_rel)] = child_seqs[idx]
                idx += 1

    for nu in nu_list:
        # Auto dt from advection CFL, clipped to remain practical.
        if args.dt is not None:
            dt = float(args.dt)
        else:
            dx = L_DOMAIN / args.N
            umax = float(np.max(np.abs(u0)))
            dt = min(0.02, 1.5 * dx / max(umax, 1e-8))

        cfg = make_solver_config(args.N, nu, dt)
        t_final_target = (args.tau_max + 0.5) * t_eddy
        times, u_hist = simulate_from_u0(u0, t_final_target, cfg)
        t_final = float(times[-1])
        u_final = u_hist[-1]
        u_final_hat = np.fft.fft(u_final)

        logger.log(
            f"[nu={nu:g}] dt={dt:.6g}, steps={len(times)-1}, "
            f"t_final={t_final:.4f} ({t_final/t_eddy:.3f} turnovers)"
        )

        for kobs_frac in kobs_frac_list:
            k_obs = args.N // kobs_frac
            obs_mask = lowpass_obs_mask(cfg.k, k_obs)
            n_obs = int(np.count_nonzero(obs_mask))
            if n_obs == 0:
                raise ValueError(f"No observed modes for kobs_frac={kobs_frac}")

            for eps_rel in eps_rel_list:
                cfg_rng = np.random.default_rng(cfg_seeds[(nu, kobs_frac, eps_rel)])
                eps = eps_rel * u_rms
                y_clean = apply_observation(u_final_hat, obs_mask)
                y_obs = add_complex_gaussian_noise(y_clean, eps, cfg_rng)

                logger.log(
                    f"  Config nu={nu:g}, k_obs=N/{kobs_frac}, eps_rel={eps_rel:g}, n_obs={n_obs}, eps={eps:.3e}"
                )

                tau_vals = []
                fwd_vals = []
                bwd_vals = []
                spread_vals = []

                for tau_req in tau_grid:
                    t_past_target = t_final - tau_req * t_eddy
                    idx_past = nearest_idx(times, t_past_target)
                    t_past = float(times[idx_past])
                    duration = t_final - t_past
                    tau_eff = duration / t_eddy

                    u_past_truth = u_hist[idx_past]

                    # Task A: forward baseline from true past.
                    u_fwd = evolve_batch(u_past_truth[None, :], duration, cfg)[0]
                    rmse_fwd = rmse_rel(u_fwd, u_final)

                    # Task B: ensemble inversion.
                    baseline_hat = np.fft.fft(u_past_truth)
                    baseline_hat *= (np.abs(cfg.k) <= 8)
                    baseline = np.fft.ifft(baseline_hat).real

                    pert0 = make_bandlimited_perturbations(
                        cfg_rng, cfg.k, (args.K, args.N), max_mode=min(32, args.N // 8), scale=0.05 * u_rms
                    )
                    candidates = baseline[None, :] + pert0
                    _, misfit = evaluate_candidates(candidates, duration, cfg, y_obs, obs_mask)

                    eps_eff = max(eps, 1e-12)
                    threshold = 2.5 * eps_eff * math.sqrt(n_obs)
                    accepted = misfit <= threshold

                    if int(np.count_nonzero(accepted)) < 8:
                        keep = max(1, args.K // 4)
                        elite_idx = np.argsort(misfit)[:keep]
                        elite = candidates[elite_idx]
                        pick = cfg_rng.integers(0, keep, size=args.K)
                        pert1 = make_bandlimited_perturbations(
                            cfg_rng, cfg.k, (args.K, args.N), max_mode=min(32, args.N // 8), scale=0.03 * u_rms
                        )
                        refined = elite[pick] + pert1
                        candidates = refined
                        _, misfit = evaluate_candidates(candidates, duration, cfg, y_obs, obs_mask)
                        accepted = misfit <= threshold

                    accepted_count = int(np.count_nonzero(accepted))
                    if accepted_count > 0:
                        acc = candidates[accepted]
                        rmse_bwd = float(np.min(np.linalg.norm(acc - u_past_truth[None, :], axis=1) / np.linalg.norm(u_past_truth)))
                        spread = float(np.mean(np.std(acc, axis=0)))
                        status = "ok"
                    else:
                        rmse_bwd = float("nan")
                        spread = float("nan")
                        status = "no_identifiable_set"

                    rows.append(
                        {
                            "nu": nu,
                            "kobs_frac": kobs_frac,
                            "eps_rel": eps_rel,
                            "tau_req": float(tau_req),
                            "tau": float(tau_eff),
                            "rmse_fwd": rmse_fwd,
                            "rmse_bwd_best": rmse_bwd,
                            "spread": spread,
                            "accepted_count": accepted_count,
                            "threshold": threshold,
                            "status": status,
                        }
                    )
                    tau_vals.append(float(tau_eff))
                    fwd_vals.append(rmse_fwd)
                    bwd_vals.append(rmse_bwd)
                    spread_vals.append(spread)

                tau_arr = np.array(tau_vals)
                fwd_arr = np.array(fwd_vals)
                bwd_arr = np.array(bwd_vals)
                spread_arr = np.array(spread_vals)
                tau_star, verdict = classify_config(tau_arr, fwd_arr, bwd_arr, spread_arr, u_rms)
                slope_fwd = fit_slope(tau_arr, fwd_arr)
                slope_bwd = fit_slope(tau_arr, bwd_arr)
                slope_ratio = None
                if slope_fwd is not None and slope_fwd != 0.0 and slope_bwd is not None:
                    slope_ratio = slope_bwd / slope_fwd

                key = f"nu={nu:g}|kobs=N/{kobs_frac}|eps={eps_rel:g}"
                summary[key] = {
                    "nu": nu,
                    "kobs_frac": kobs_frac,
                    "eps_rel": eps_rel,
                    "tau_star": tau_star,
                    "verdict": verdict,
                    "slope_fwd": slope_fwd,
                    "slope_bwd": slope_bwd,
                    "slope_ratio_bwd_over_fwd": slope_ratio,
                    "max_spread": float(np.nanmax(spread_arr)) if np.any(np.isfinite(spread_arr)) else None,
                }
                logger.log(
                    f"    Verdict: {verdict}; tau*={tau_star}; "
                    f"slope_ratio={None if slope_ratio is None else round(float(slope_ratio), 3)}"
                )

    df = pd.DataFrame(rows).sort_values(["nu", "kobs_frac", "eps_rel", "tau"])
    metrics_path = out_dir / "metrics.csv"
    df.to_csv(metrics_path, index=False)

    plot_metric(df, "rmse_fwd", "Forward RMSE vs tau", "RMSE_fwd", out_dir / "plot_rmse_fwd.png")
    plot_metric(df, "rmse_bwd_best", "Backward RMSE (best) vs tau", "RMSE_bwd_best", out_dir / "plot_rmse_bwd.png")
    plot_metric(df, "spread", "Accepted-ensemble Spread vs tau", "Spread", out_dir / "plot_spread.png")

    summary_obj = {
        "seed": args.seed,
        "N": args.N,
        "K": args.K,
        "nu_list": nu_list,
        "kobs_frac_list": kobs_frac_list,
        "eps_rel_list": eps_rel_list,
        "tau_grid_requested": [float(x) for x in tau_grid],
        "u_rms": u_rms,
        "t_eddy": t_eddy,
        "configs": summary,
    }
    write_summary(out_dir / "summary.json", summary_obj)

    logger.log(f"Saved metrics to: {metrics_path}")
    logger.log(f"Saved summary to: {out_dir / 'summary.json'}")
    logger.log(f"Saved plots to: {out_dir}")
    logger.close()


if __name__ == "__main__":
    main()
