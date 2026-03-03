#!/usr/bin/env python3
"""Setup 3 strict reproduction runner."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import time
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import odeint


L_DOMAIN = 2.0 * math.pi


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
    kabs: np.ndarray
    dealias: np.ndarray


def parse_csv_floats(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def make_spectral2d(n: int) -> Spectral2D:
    k1 = np.fft.fftfreq(n, d=1.0 / n)
    kx, ky = np.meshgrid(k1, k1, indexing="xy")
    k2 = kx * kx + ky * ky
    kabs = np.sqrt(k2)
    kcut = n // 3
    dealias = ((np.abs(kx) <= kcut) & (np.abs(ky) <= kcut)).astype(float)
    return Spectral2D(n=n, kx=kx, ky=ky, k2=k2, kabs=kabs, dealias=dealias)


def rel_l2(a: np.ndarray, b: np.ndarray) -> float:
    d = np.linalg.norm(a - b)
    n = np.linalg.norm(b)
    if n == 0:
        return float("nan")
    return float(d / n)


def nearest_idx(times: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(times - target)))


def make_initial_vorticity(spec: Spectral2D, seed: int, n_vortices: int = 8) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, L_DOMAIN, spec.n, endpoint=False)
    xg, yg = np.meshgrid(x, x, indexing="xy")
    omega = np.zeros((spec.n, spec.n), dtype=float)
    sigma = 0.22
    for _ in range(n_vortices):
        cx = rng.uniform(0.0, L_DOMAIN)
        cy = rng.uniform(0.0, L_DOMAIN)
        amp = rng.uniform(-2.0, 2.0)
        dx = np.minimum(np.abs(xg - cx), L_DOMAIN - np.abs(xg - cx))
        dy = np.minimum(np.abs(yg - cy), L_DOMAIN - np.abs(yg - cy))
        omega += amp * np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))
    omega -= np.mean(omega)
    omega /= max(float(np.std(omega)), 1e-12)
    return omega


def velocity_from_omega(omega_hat: np.ndarray, spec: Spectral2D) -> tuple[np.ndarray, np.ndarray]:
    inv_k2 = np.zeros_like(spec.k2)
    mask = spec.k2 > 0
    inv_k2[mask] = 1.0 / spec.k2[mask]
    psi_hat = -omega_hat * inv_k2
    u = np.fft.ifft2(1j * spec.ky * psi_hat).real
    v = np.fft.ifft2(-1j * spec.kx * psi_hat).real
    return u, v


def burgers_rhs_flat(omega_flat: np.ndarray, _t: float, nu: float, spec: Spectral2D) -> np.ndarray:
    n = spec.n
    omega = omega_flat.reshape((n, n))
    omega_hat = np.fft.fft2(omega)
    u, v = velocity_from_omega(omega_hat, spec)
    dwdx = np.fft.ifft2(1j * spec.kx * omega_hat).real
    dwdy = np.fft.ifft2(1j * spec.ky * omega_hat).real
    adv = u * dwdx + v * dwdy
    adv_hat = np.fft.fft2(adv) * spec.dealias
    visc_hat = -nu * spec.k2 * omega_hat
    domega_hat = -adv_hat + visc_hat
    domega = np.fft.ifft2(domega_hat).real
    return domega.ravel()


def integrate_field(
    omega0: np.ndarray,
    times: np.ndarray,
    nu: float,
    spec: Spectral2D,
    max_steps: int,
) -> tuple[np.ndarray, int]:
    warning_count = 0
    hspan = abs(float(times[-1] - times[0]))
    hmax = hspan / max(20, len(times) - 1)
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        out = odeint(
            burgers_rhs_flat,
            omega0.ravel(),
            times,
            args=(nu, spec),
            mxstep=max_steps,
            atol=1e-5,
            rtol=1e-4,
            hmax=hmax,
        )
    warning_count += len(rec)
    hist = out.reshape((len(times), spec.n, spec.n))
    return hist, warning_count


def spectral_info_bits(omega: np.ndarray) -> float:
    power = np.abs(np.fft.fft2(omega)) ** 2
    peak = float(np.max(power))
    if peak <= 0.0:
        return 0.0
    active = int(np.count_nonzero(power >= 1e-6 * peak))
    return float(np.log2(max(active, 1)))


def build_figure(
    out_path: Path,
    test1_df: pd.DataFrame,
    t2: np.ndarray,
    info_bits: np.ndarray,
    loss_rate: np.ndarray,
    critical_threshold: float,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    ax = axes[0, 0]
    ax.plot(test1_df["Re"], test1_df["ratio"], marker="o", linewidth=2)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.axhline(3.0, color="red", linestyle="--", linewidth=1)
    ax.set_xscale("log")
    ax.set_xlabel("Re")
    ax.set_ylabel("Backward/Forward Error Ratio")
    ax.set_title("Error Ratio vs Reynolds Number")
    ax.grid(alpha=0.3)

    ax = axes[0, 1]
    ax.plot(test1_df["Re"], test1_df["forward_error"], marker="o", label="Forward Error")
    ax.plot(test1_df["Re"], test1_df["backward_error"], marker="s", label="Backward Error")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Re")
    ax.set_ylabel("Relative L2 Error")
    ax.set_title("Absolute Errors vs Reynolds Number")
    ax.grid(alpha=0.3)
    ax.legend()

    ax = axes[1, 0]
    ax.plot(t2, info_bits, linewidth=2)
    ax.set_xlabel("Time")
    ax.set_ylabel("Information Content (bits)")
    ax.set_title("Spectral Information Decay")
    ax.grid(alpha=0.3)

    ax = axes[1, 1]
    ax.plot(t2, loss_rate, linewidth=2)
    ax.axhline(critical_threshold, color="red", linestyle="--", linewidth=1, label="Critical Threshold")
    ax.set_xlabel("Time")
    ax.set_ylabel("Information Loss Rate (bits/time)")
    ax.set_title("Information Loss Rate")
    ax.grid(alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_path, dpi=170)
    plt.close(fig)


def run_test1(
    spec: Spectral2D,
    omega0: np.ndarray,
    re_list: list[float],
    t_total: float,
    horizon: float,
    noise_rel: float,
    max_steps: int,
    seed: int,
    logger: TeeLogger,
) -> tuple[pd.DataFrame, int]:
    rng = np.random.default_rng(seed + 9_001)
    records = []
    warning_count = 0
    times_truth = np.linspace(0.0, t_total, 160)

    t_present = t_total / 2.0
    t_past = t_present - horizon
    t_future = t_present + horizon
    if t_past < 0.0 or t_future > t_total:
        raise ValueError("t_total_test1 must contain present +/- horizon")

    for re in re_list:
        nu = 1.0 / re
        truth_hist, wc = integrate_field(omega0, times_truth, nu=nu, spec=spec, max_steps=max_steps)
        warning_count += wc
        i_present = nearest_idx(times_truth, t_present)
        i_past = nearest_idx(times_truth, t_past)
        i_future = nearest_idx(times_truth, t_future)

        w_present_true = truth_hist[i_present]
        w_past_true = truth_hist[i_past]
        w_future_true = truth_hist[i_future]

        noisy_present = w_present_true + noise_rel * np.std(w_present_true) * rng.normal(size=w_present_true.shape)

        t_fwd = np.linspace(t_present, t_future, 64)
        fwd_hist, wc = integrate_field(noisy_present, t_fwd, nu=nu, spec=spec, max_steps=max_steps)
        warning_count += wc
        w_future_pred = fwd_hist[-1]

        t_bwd = np.linspace(t_present, t_past, 64)
        bwd_hist, wc = integrate_field(noisy_present, t_bwd, nu=nu, spec=spec, max_steps=max_steps)
        warning_count += wc
        w_past_recon = bwd_hist[-1]

        forward_error = rel_l2(w_future_pred, w_future_true)
        backward_error = rel_l2(w_past_recon, w_past_true)
        ratio = backward_error / max(forward_error, 1e-14)
        records.append(
            {
                "Re": int(re),
                "forward_error": float(forward_error),
                "backward_error": float(backward_error),
                "ratio": float(ratio),
            }
        )
        logger.log(
            f"[test1] Re={re:g}, fwd={forward_error:.6g}, bwd={backward_error:.6g}, ratio={ratio:.4g}"
        )

    df = pd.DataFrame(records).sort_values("Re")
    return df, warning_count


def run_test2(
    spec: Spectral2D,
    omega0: np.ndarray,
    t_total: float,
    snapshots: int,
    max_steps: int,
    logger: TeeLogger,
) -> tuple[pd.DataFrame, dict, int]:
    re = 2000.0
    nu = 1.0 / re
    t = np.linspace(0.0, t_total, snapshots)
    hist, warning_count = integrate_field(omega0, t, nu=nu, spec=spec, max_steps=max_steps)

    info_bits = np.array([spectral_info_bits(w) for w in hist])
    loss_rate = -np.gradient(info_bits, t)
    capacity0 = float(info_bits[0])
    critical = 0.15 * capacity0
    threshold_crossed = bool(np.any(loss_rate >= critical))

    w0_hat = np.fft.fft2(hist[0])
    u0, v0 = velocity_from_omega(w0_hat, spec)
    u_rms = float(np.sqrt(np.mean(u0 * u0 + v0 * v0)))
    integral_len = L_DOMAIN / 2.0
    eddy_turnover = integral_len / max(u_rms, 1e-12)

    logger.log(
        f"[test2] Re=2000, info(0)={capacity0:.4f}, info(T)={info_bits[-1]:.4f}, "
        f"loss_avg={np.mean(loss_rate):.4f}, critical={critical:.4f}"
    )

    series = pd.DataFrame(
        {
            "time": t,
            "info_bits": info_bits,
            "loss_rate": loss_rate,
            "critical_threshold": np.full_like(t, critical),
        }
    )
    stats = {
        "initial_info_bits": capacity0,
        "final_info_bits": float(info_bits[-1]),
        "avg_loss_rate": float(np.mean(loss_rate)),
        "max_loss_rate": float(np.max(loss_rate)),
        "critical_threshold": float(critical),
        "threshold_crossed": threshold_crossed,
        "eddy_turnover_time": float(eddy_turnover),
    }
    return series, stats, warning_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Setup 3 strict reproduction.")
    parser.add_argument("--outdir", default="results")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--re-list", default="100,500,2000,5000")
    parser.add_argument("--noise-rel", type=float, default=0.02)
    parser.add_argument("--horizon", type=float, default=1.0)
    parser.add_argument("--t-total-test1", type=float, default=3.0)
    parser.add_argument("--t-total-test2", type=float, default=5.0)
    parser.add_argument("--snapshots-test2", type=int, default=100)
    parser.add_argument("--max-steps", type=int, default=5000)
    parser.add_argument("--overwrite-canonical", type=lambda x: str(x).lower() == "true", default=True)
    args = parser.parse_args()

    started = time.time()
    here = Path(__file__).resolve().parent
    out_root = (here / args.outdir).resolve()
    run_dir = out_root / datetime.now().strftime("%Y%m%d_%H%M%S")
    ensure_dir(run_dir)
    logger = TeeLogger(run_dir / "run.log")
    logger.log(f"Output directory: {run_dir}")
    logger.log(f"Arguments: {vars(args)}")

    spec = make_spectral2d(args.N)
    omega0 = make_initial_vorticity(spec, seed=args.seed)

    re_list = parse_csv_floats(args.re_list)
    test1_df, w1 = run_test1(
        spec=spec,
        omega0=omega0,
        re_list=re_list,
        t_total=args.t_total_test1,
        horizon=args.horizon,
        noise_rel=args.noise_rel,
        max_steps=args.max_steps,
        seed=args.seed,
        logger=logger,
    )
    test1_path = run_dir / "reconstruction_test_results.csv"
    test1_df.to_csv(test1_path, index=False)

    test2_series, test2_stats, w2 = run_test2(
        spec=spec,
        omega0=omega0,
        t_total=args.t_total_test2,
        snapshots=args.snapshots_test2,
        max_steps=args.max_steps,
        logger=logger,
    )
    test2_path = run_dir / "test2_information_series.csv"
    test2_series.to_csv(test2_path, index=False)

    fig_path = run_dir / "navier_stokes_reconstruction_asymmetry.png"
    build_figure(
        out_path=fig_path,
        test1_df=test1_df,
        t2=test2_series["time"].to_numpy(),
        info_bits=test2_series["info_bits"].to_numpy(),
        loss_rate=test2_series["loss_rate"].to_numpy(),
        critical_threshold=float(test2_series["critical_threshold"].iloc[0]),
    )

    old_csv = here / "reconstruction_test_results.csv"
    reproduction: dict[str, object] = {
        "matched_re_values": [],
        "max_abs_delta_ratio": None,
    }
    if old_csv.exists():
        try:
            prev = pd.read_csv(str(old_csv))
            merged = prev.merge(test1_df, on="Re", suffixes=("_old", "_new"))
            if len(merged):
                deltas = np.abs(merged["ratio_old"] - merged["ratio_new"])
                reproduction["matched_re_values"] = [int(x) for x in merged["Re"].tolist()]
                reproduction["max_abs_delta_ratio"] = float(np.max(deltas))
        except Exception as exc:
            logger.log(f"Could not compare with existing CSV: {exc}")

    if args.overwrite_canonical:
        shutil.copy2(test1_path, here / "reconstruction_test_results.csv")
        shutil.copy2(fig_path, here / "navier_stokes_reconstruction_asymmetry.png")
        logger.log("Updated canonical setup_3 root CSV and PNG.")

    ratios = test1_df["ratio"].to_numpy()
    monotonic = bool(np.all(np.diff(ratios) >= -1e-10))
    ratio_at_5000 = float(test1_df.loc[test1_df["Re"] == 5000, "ratio"].iloc[0]) if np.any(test1_df["Re"] == 5000) else None
    if ratio_at_5000 is not None and ratio_at_5000 >= 3.0 and monotonic:
        overall = "Supported"
    elif np.all(ratios > 1.0):
        overall = "Partial"
    else:
        overall = "Inconclusive"

    summary = {
        "run_config": vars(args),
        "runtime_seconds": float(time.time() - started),
        "numeric_warning_count": int(w1 + w2),
        "test1": {
            "rows": test1_df.to_dict(orient="records"),
            "ratio_monotonic_with_re": monotonic,
            "ratio_at_re5000": ratio_at_5000,
        },
        "test2": test2_stats,
        "reproduction_vs_existing": reproduction,
        "overall_interpretation": overall,
    }
    with (run_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    logger.log(f"Saved: {test1_path}")
    logger.log(f"Saved: {test2_path}")
    logger.log(f"Saved: {fig_path}")
    logger.log(f"Saved: {run_dir / 'summary.json'}")
    logger.close()


if __name__ == "__main__":
    main()
