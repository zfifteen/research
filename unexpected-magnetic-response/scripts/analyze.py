#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"


def load_observations() -> dict[str, float]:
    df = pd.read_csv(DATA_DIR / "paper_observations.csv")
    values: dict[str, float] = {}
    for row in df.itertuples(index=False):
        if isinstance(row.value, (int, float)):
            values[row.quantity] = float(row.value)
    return values


def required_occupancy(mean_conductance: np.ndarray, state_conductance: np.ndarray) -> np.ndarray:
    return (1.0 - mean_conductance) / (1.0 - state_conductance)


def conductance_from_occupancy(occupancy: np.ndarray, state_conductance: float) -> np.ndarray:
    return 1.0 - occupancy * (1.0 - state_conductance)


def boltzmann_bias(energy_scale_ev: np.ndarray, temperature_k: float) -> np.ndarray:
    k_b_ev = 8.617333262145e-5
    return np.exp(energy_scale_ev / (k_b_ev * temperature_k))


def ensure_output_dirs() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    FIG_DIR.mkdir(exist_ok=True)


def set_plot_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "font.size": 10,
        }
    )


def plot_required_occupancy(target_mean: float, chosen_state: float) -> dict[str, float]:
    g_state = np.linspace(0.4, 0.98, 400)
    p_needed = required_occupancy(np.full_like(g_state, target_mean), g_state)
    feasible = p_needed <= 1.0

    fig, ax = plt.subplots(figsize=(8.5, 5.3))
    ax.plot(g_state, p_needed, color="#ab3b3a", lw=2.5)
    ax.fill_between(g_state, p_needed, 1.0, where=feasible, color="#f4c7c3", alpha=0.6)
    ax.axhline(1.0, color="black", ls="--", lw=1.1)
    ax.axvline(chosen_state, color="#1d6996", ls="--", lw=1.1)
    ax.scatter([chosen_state], [required_occupancy(np.array([target_mean]), np.array([chosen_state]))[0]],
               color="#1d6996", s=70, zorder=3)
    ax.set_xlim(0.4, 0.98)
    ax.set_ylim(0.0, 3.1)
    ax.set_xlabel("Conductance of oxygen-assisted state (G/G0)")
    ax.set_ylabel("Required high-field occupancy")
    ax.set_title("Occupancy Required To Reach Mean Conductance 0.85 G0")
    ax.text(
        0.61,
        2.25,
        "Above the dashed line, the model is impossible\nbecause occupancy would exceed 100%.",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.95},
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "occupancy_required_vs_state_conductance.png")
    plt.close(fig)

    p_chosen = float(required_occupancy(np.array([target_mean]), np.array([chosen_state]))[0])
    return {
        "target_mean_conductance": target_mean,
        "chosen_oxygen_state_conductance": chosen_state,
        "required_occupancy_at_chosen_state": p_chosen,
        "max_state_conductance_for_feasibility": float(target_mean),
    }


def plot_mean_conductance_vs_occupancy() -> dict[str, float]:
    occupancy = np.linspace(0.0, 1.0, 300)
    states = [0.6, 0.7, 0.8, 0.85]
    colors = ["#0f4c5c", "#2c7a7b", "#84a59d", "#f6bd60"]

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    crossing_points: dict[str, float] = {}
    for g_state, color in zip(states, colors):
        mean_g = conductance_from_occupancy(occupancy, g_state)
        ax.plot(occupancy, mean_g, lw=2.4, color=color, label=f"State = {g_state:.2f} G0")
        needed = float(required_occupancy(np.array([0.85]), np.array([g_state]))[0])
        if needed <= 1.0:
            crossing_points[f"{g_state:.2f}"] = needed
            ax.scatter([needed], [0.85], color=color, s=45, zorder=3)

    ax.axhline(0.85, color="black", ls="--", lw=1.0, label="Observed high-field level")
    ax.set_xlabel("High-field occupancy of low-conductance state")
    ax.set_ylabel("Mean conductance (G/G0)")
    ax.set_title("Mean Conductance Is Highly Sensitive To Occupancy")
    ax.set_ylim(0.55, 1.01)
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "mean_conductance_vs_occupancy.png")
    plt.close(fig)
    return crossing_points


def plot_orientation_bias(temperature_k: float, mae_ev: float) -> dict[str, float]:
    energy = np.linspace(0.0, 5e-4, 300)
    bias = boltzmann_bias(energy, temperature_k)

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ax.plot(energy * 1e4, bias, color="#3d405b", lw=2.6)
    ax.axvline(mae_ev * 1e4, color="#e07a5f", ls="--", lw=1.1)
    chosen_bias = float(boltzmann_bias(np.array([mae_ev]), temperature_k)[0])
    ax.scatter([mae_ev * 1e4], [chosen_bias], color="#e07a5f", s=60, zorder=3)
    ax.set_xlabel("Energy bias (x10^-4 eV)")
    ax.set_ylabel("Boltzmann occupancy ratio")
    ax.set_title(f"Simple Orientation Bias At {temperature_k:.1f} K")
    ax.text(
        2.6,
        1.27,
        "An energy scale near 1e-4 eV gives only\nmodest thermal preference at 4.2 K.",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.95},
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "orientation_bias_vs_energy.png")
    plt.close(fig)
    return {
        "temperature_k": temperature_k,
        "chosen_energy_bias_ev": mae_ev,
        "boltzmann_ratio_at_chosen_energy": chosen_bias,
    }


def gaussian(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2.0 * np.pi))


def plot_example_histograms() -> dict[str, float]:
    x = np.linspace(0.55, 1.05, 600)
    sigma = 0.018

    p_low = 0.05
    p_high = 0.75
    low_field = (1.0 - p_low) * gaussian(x, 1.0, sigma) + p_low * gaussian(x, 0.8, sigma)
    high_field = (1.0 - p_high) * gaussian(x, 1.0, sigma) + p_high * gaussian(x, 0.8, sigma)

    fig, ax = plt.subplots(figsize=(8.6, 5.3))
    ax.plot(x, low_field, color="#2a9d8f", lw=2.5, label="Low field example")
    ax.plot(x, high_field, color="#e76f51", lw=2.5, label="High field example")
    ax.axvline(1.0, color="black", lw=0.8, ls=":")
    ax.axvline(0.8, color="black", lw=0.8, ls=":")
    ax.set_xlabel("Conductance (G/G0)")
    ax.set_ylabel("Relative density")
    ax.set_title("Illustrative Histogram Shift Needed In A Two-State Model")
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "example_histograms.png")
    plt.close(fig)
    return {"example_low_field_occupancy": p_low, "example_high_field_occupancy": p_high}


def write_summary(metrics: dict[str, object]) -> None:
    with (OUTPUT_DIR / "summary_metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, sort_keys=True)


def main() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
    ensure_output_dirs()
    set_plot_style()

    obs = load_observations()
    target_mean = obs["au_high_field_gb"]
    oxygen_state = obs["oxygen_state_conductance"]
    temperature_k = obs["temperature"]
    mae_ev = obs["mae_order"]

    occupancy_metrics = plot_required_occupancy(target_mean, oxygen_state)
    sensitivity_metrics = plot_mean_conductance_vs_occupancy()
    orientation_metrics = plot_orientation_bias(temperature_k, mae_ev)
    histogram_metrics = plot_example_histograms()

    summary = {
        "project": "unexpected-magnetic-response",
        "headline_result": (
            "A 0.8 G0 oxygen-assisted state requires 75 percent high-field occupancy "
            "to produce a mean conductance of 0.85 G0 in a two-state model."
        ),
        "occupancy_metrics": occupancy_metrics,
        "sensitivity_crossings": sensitivity_metrics,
        "orientation_metrics": orientation_metrics,
        "histogram_example": histogram_metrics,
    }
    write_summary(summary)

    print("Generated figures:")
    for path in sorted(FIG_DIR.glob("*.png")):
        print(f"- {path.relative_to(ROOT)}")
    print("Wrote outputs/summary_metrics.json")


if __name__ == "__main__":
    main()
