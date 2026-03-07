
#!/usr/bin/env python3
"""
Green Paper
===========

Replication–Communication Competition in the Gray–Scott System
and the Emergent Replication Péclet Number

This file is intentionally written as a runnable Python white paper.
It mixes natural-language explanation, derivation notes, theorem-style
claims, and numerical experiments that generate a large set of 2D plots.

Core hypothesis
---------------
Chaotic spot dynamics in the Gray–Scott system emerge when discrete
replication events outrun the speed at which the substrate field can
communicate spatial information across a typical neighbor spacing.

The proposed emergent control quantity is the Replication Péclet number

    Pe_r = L^2 / (D_u * tau_r),

where
    L      : characteristic nearest-neighbor spacing,
    D_u    : substrate diffusivity,
    tau_r  : mean replication time.

Interpretation
--------------
Pe_r is the number of replication windows that fit inside one diffusive
communication time across one neighbor gap. When Pe_r is small, spots
have time to communicate and organize. When Pe_r is order one or larger,
new births happen before inhibitory and recovery fields can coordinate
spacing, so order is repeatedly broken before it can settle.

What this script does
---------------------
1. Derives and visualizes the emergent quantity with reduced-model plots.
2. Builds a refined signaling action that includes feed relaxation.
3. Converts the criterion into a probability of "birth before coordination".
4. Runs a lightweight Gray–Scott simulation at fixed reaction kinetics
   while varying D_u alone, to illustrate the proposed orthogonal
   control axis.
5. Saves copious 2D plots and prints a short result summary.

Important scope note
--------------------
This script is a green paper, not a proof of the full Gray–Scott PDE.
The reduced-model derivations are rigorous at their own level. The PDE
experiment is illustrative support.

References
----------
[1] J. E. Pearson, "Complex patterns in a simple system," Science 261,
    189-192 (1993). DOI: 10.1126/science.261.5118.189
[2] K.-J. Lee, W. D. McCormick, J. E. Pearson, H. L. Swinney,
    "Experimental observation of self-replicating spots in a
    reaction-diffusion system," Nature 369, 215-218 (1994).
    DOI: 10.1038/369215a0
[3] Y. Nishiura and D. Ueyama, "Spatio-temporal chaos for the Gray-Scott
    model," Physica D 150, 137-162 (2001).
    DOI: 10.1016/S0167-2789(00)00214-1
[4] H. Wang and Q. Ouyang, "Spatiotemporal Chaos of Self-Replicating
    Spots in Reaction-Diffusion Systems," Phys. Rev. Lett. 99, 214102
    (2007). DOI: 10.1103/PhysRevLett.99.214102
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Section 1. Plain-language statement of the hypothesis
# ---------------------------------------------------------------------------

NARRATIVE = """
Green paper thesis
------------------
The Gray–Scott system supports localized activator spots that consume
substrate locally. A spot can replicate through a local instability,
but neighboring spots can only communicate through the substrate field.

That immediately creates a race:

    local birth of new structure  versus  nonlocal diffusive signaling.

If birth wins, the lattice never gets enough time to enforce spacing.
If signaling wins, local replication can still happen, but the pattern
has time to settle into an ordered arrangement.

That race is naturally summarized by the emergent quantity

    Pe_r = L^2 / (D_u * tau_r).

This is why the quantity is appealing: it is not a parameter inserted
from outside. It emerges from the communication time L^2 / D_u and the
local replication time tau_r. The ratio is the control variable.

Reduced-model laws used here
----------------------------
1. Communication time across one neighbor gap:
       t_comm ~ L^2 / D_u

2. Replication Péclet number:
       Pe_r = t_comm / tau_r = L^2 / (D_u * tau_r)

3. Reduced probability that at least one uncoordinated birth occurs
   before communication:
       P_unc = 1 - exp(-Pe_r)

4. Outer-region substrate signaling kernel over one replication window:
       G(L, tau_r) ~ exp[-L^2 / (4 D_u tau_r) - F tau_r]
                     / (4 pi D_u tau_r)

The final formula shows why Pe_r is not arbitrary. It appears inside the
transport exponent of the linearized substrate communication kernel.
"""


# ---------------------------------------------------------------------------
# Section 2. Reduced-model quantities
# ---------------------------------------------------------------------------

def replication_peclet(L: np.ndarray, Du: np.ndarray, tau_r: np.ndarray) -> np.ndarray:
    """Emergent transport-vs-replication control quantity."""
    return (L ** 2) / (Du * tau_r)


def uncoordinated_birth_probability(Pe_r: np.ndarray) -> np.ndarray:
    """
    Renewal-model interpretation:
    probability that at least one replication event occurs before
    diffusive coordination across one gap completes.
    """
    return 1.0 - np.exp(-Pe_r)


def signaling_kernel_amplitude(
    L: np.ndarray,
    Du: np.ndarray,
    tau_r: np.ndarray,
    F: float,
) -> np.ndarray:
    """
    Leading-order outer-region substrate signaling amplitude.
    This is not a full Green's function normalization study; it is the
    reduced quantity needed for the green paper.
    """
    prefactor = 1.0 / (4.0 * math.pi * Du * tau_r)
    exponent = -(L ** 2) / (4.0 * Du * tau_r) - F * tau_r
    return prefactor * np.exp(exponent)


def refined_signaling_action(
    L: np.ndarray,
    Du: np.ndarray,
    tau_r: np.ndarray,
    F: float,
) -> np.ndarray:
    """
    Dimensionless barrier in the outer linearized substrate field:
        A_sig = L^2 / (4 D_u tau_r) + F tau_r
    """
    return (L ** 2) / (4.0 * Du * tau_r) + F * tau_r


# ---------------------------------------------------------------------------
# Section 3. Plot helpers
# ---------------------------------------------------------------------------

def style_axes(ax, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def save_heatmap(
    Z: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    title: str,
    xlabel: str,
    ylabel: str,
    colorbar_label: str,
    filepath: Path,
    *,
    contour_level: float | None = None,
    contour_color: str = "white",
    cmap: str = "viridis",
    vmin: float | None = None,
    vmax: float | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(
        Z,
        origin="lower",
        aspect="auto",
        extent=[x.min(), x.max(), y.min(), y.max()],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
    )
    if contour_level is not None:
        X, Y = np.meshgrid(x, y)
        cs = ax.contour(
            X,
            Y,
            Z,
            levels=[contour_level],
            colors=contour_color,
            linewidths=1.5,
        )
        ax.clabel(cs, inline=True, fontsize=9, fmt={contour_level: f"{contour_level:g}"})
    style_axes(ax, title, xlabel, ylabel)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(colorbar_label)
    fig.tight_layout()
    fig.savefig(filepath, dpi=180)
    plt.close(fig)


def save_field_image(
    field: np.ndarray,
    title: str,
    filepath: Path,
    *,
    cmap: str = "viridis",
    colorbar_label: str = "value",
) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 6))
    im = ax.imshow(field, origin="lower", cmap=cmap)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=12)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(colorbar_label)
    fig.tight_layout()
    fig.savefig(filepath, dpi=180)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Section 4. Lightweight Gray–Scott simulator
# ---------------------------------------------------------------------------

def laplacian_periodic(z: np.ndarray) -> np.ndarray:
    return (
        np.roll(z, 1, axis=0)
        + np.roll(z, -1, axis=0)
        + np.roll(z, 1, axis=1)
        + np.roll(z, -1, axis=1)
        - 4.0 * z
    )


def initialize_gray_scott(n: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    u = np.ones((n, n), dtype=np.float64)
    v = np.zeros((n, n), dtype=np.float64)

    r = n // 10
    c = n // 2
    u[c - r:c + r, c - r:c + r] = 0.50
    v[c - r:c + r, c - r:c + r] = 0.25

    u += 0.01 * rng.standard_normal((n, n))
    v += 0.01 * rng.standard_normal((n, n))
    np.clip(u, 0.0, 1.5, out=u)
    np.clip(v, 0.0, 1.5, out=v)
    return u, v


def spatial_entropy(field: np.ndarray, bins: int = 48) -> float:
    lo = float(field.min())
    hi = float(field.max()) + 1e-12
    hist, _ = np.histogram(field, bins=bins, range=(lo, hi))
    p = hist.astype(np.float64)
    total = p.sum()
    if total <= 0:
        return 0.0
    p /= total
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def gradient_energy(field: np.ndarray) -> float:
    gx = np.roll(field, -1, axis=1) - field
    gy = np.roll(field, -1, axis=0) - field
    return float(np.mean(gx * gx + gy * gy))


def active_area(field: np.ndarray, threshold: float = 0.25) -> float:
    return float(np.mean(field > threshold))


def simulate_gray_scott(
    Du: float,
    Dv: float,
    F: float,
    k: float,
    *,
    n: int,
    steps: int,
    dt: float,
    sample_every: int,
    seed: int,
) -> dict[str, np.ndarray]:
    u, v = initialize_gray_scott(n, seed)

    times = []
    entropy_series = []
    gradient_series = []
    area_series = []

    for step in range(steps):
        uvv = u * v * v
        u += dt * (Du * laplacian_periodic(u) - uvv + F * (1.0 - u))
        v += dt * (Dv * laplacian_periodic(v) + uvv - (F + k) * v)

        np.clip(u, 0.0, 2.0, out=u)
        np.clip(v, 0.0, 2.0, out=v)

        if step % sample_every == 0 or step == steps - 1:
            times.append(step * dt)
            entropy_series.append(spatial_entropy(v))
            gradient_series.append(gradient_energy(v))
            area_series.append(active_area(v))

    return {
        "u_final": u,
        "v_final": v,
        "times": np.asarray(times, dtype=np.float64),
        "entropy": np.asarray(entropy_series, dtype=np.float64),
        "gradient_energy": np.asarray(gradient_series, dtype=np.float64),
        "active_area": np.asarray(area_series, dtype=np.float64),
    }


# ---------------------------------------------------------------------------
# Section 5. Green-paper plot program
# ---------------------------------------------------------------------------

def build_reduced_model_figures(output_dir: Path) -> list[Path]:
    files: list[Path] = []

    # Parameter windows used only to visualize the reduced criterion.
    L = np.linspace(0.2, 3.0, 280)
    Du = np.linspace(0.02, 0.30, 260)
    tau = np.linspace(0.2, 8.0, 260)

    L1, Du1 = np.meshgrid(L, Du)
    tau_fixed = 1.5
    F_fixed = 0.04

    Pe_L_Du = replication_peclet(L1, Du1, tau_fixed)
    P_unc_L_Du = uncoordinated_birth_probability(Pe_L_Du)
    G_L_Du = signaling_kernel_amplitude(L1, Du1, tau_fixed, F_fixed)
    A_sig_L_Du = refined_signaling_action(L1, Du1, tau_fixed, F_fixed)

    path = output_dir / "01_pe_r_L_vs_Du.png"
    save_heatmap(
        Pe_L_Du, L, Du,
        title=r"Replication Péclet number $Pe_r = L^2 / (D_u \tau_r)$ at fixed $\tau_r$",
        xlabel="inter-spot spacing L",
        ylabel="substrate diffusivity D_u",
        colorbar_label="Pe_r",
        filepath=path,
        contour_level=1.0,
        cmap="magma",
    )
    files.append(path)

    path = output_dir / "02_probability_uncoordinated_birth_L_vs_Du.png"
    save_heatmap(
        P_unc_L_Du, L, Du,
        title=r"Probability of birth before coordination: $1-e^{-Pe_r}$",
        xlabel="inter-spot spacing L",
        ylabel="substrate diffusivity D_u",
        colorbar_label="P_unc",
        filepath=path,
        contour_level=1.0 - math.e ** -1.0,
        cmap="viridis",
        vmin=0.0,
        vmax=1.0,
    )
    files.append(path)

    path = output_dir / "03_signaling_amplitude_L_vs_Du.png"
    save_heatmap(
        np.log10(G_L_Du + 1e-18), L, Du,
        title=r"Log signaling amplitude over one replication window",
        xlabel="inter-spot spacing L",
        ylabel="substrate diffusivity D_u",
        colorbar_label=r"$\log_{10} G(L,\tau_r)$",
        filepath=path,
        cmap="plasma",
    )
    files.append(path)

    path = output_dir / "04_refined_signaling_action_L_vs_Du.png"
    save_heatmap(
        A_sig_L_Du, L, Du,
        title=r"Refined signaling action $L^2/(4D_u\tau_r) + F\tau_r$",
        xlabel="inter-spot spacing L",
        ylabel="substrate diffusivity D_u",
        colorbar_label="action",
        filepath=path,
        contour_level=1.0,
        cmap="cividis",
    )
    files.append(path)

    # L versus tau_r at fixed diffusivity.
    L2, Tau2 = np.meshgrid(L, tau)
    Du_fixed = 0.12
    Pe_L_tau = replication_peclet(L2, Du_fixed, Tau2)
    P_unc_L_tau = uncoordinated_birth_probability(Pe_L_tau)

    path = output_dir / "05_pe_r_L_vs_tau_r.png"
    save_heatmap(
        Pe_L_tau, L, tau,
        title=r"Replication Péclet number across spacing and replication time",
        xlabel="inter-spot spacing L",
        ylabel=r"replication time $\tau_r$",
        colorbar_label="Pe_r",
        filepath=path,
        contour_level=1.0,
        cmap="magma",
    )
    files.append(path)

    path = output_dir / "06_probability_uncoordinated_birth_L_vs_tau_r.png"
    save_heatmap(
        P_unc_L_tau, L, tau,
        title=r"Birth-before-coordination probability across L and $\tau_r$",
        xlabel="inter-spot spacing L",
        ylabel=r"replication time $\tau_r$",
        colorbar_label="P_unc",
        filepath=path,
        contour_level=1.0 - math.e ** -1.0,
        cmap="viridis",
        vmin=0.0,
        vmax=1.0,
    )
    files.append(path)

    # Sensitivity maps.
    dPe_dDu = -(L1 ** 2) / (tau_fixed * (Du1 ** 2))
    dPe_dL = 2.0 * L1 / (Du1 * tau_fixed)

    path = output_dir / "07_sensitivity_abs_dPe_dDu_L_vs_Du.png"
    save_heatmap(
        np.log10(np.abs(dPe_dDu) + 1e-12), L, Du,
        title=r"Log sensitivity magnitude $\left|\partial Pe_r/\partial D_u\right|$",
        xlabel="inter-spot spacing L",
        ylabel="substrate diffusivity D_u",
        colorbar_label=r"$\log_{10}\left|\partial Pe_r/\partial D_u\right|$",
        filepath=path,
        cmap="inferno",
    )
    files.append(path)

    path = output_dir / "08_sensitivity_dPe_dL_L_vs_Du.png"
    save_heatmap(
        dPe_dL, L, Du,
        title=r"Sensitivity $\partial Pe_r/\partial L = 2L/(D_u\tau_r)$",
        xlabel="inter-spot spacing L",
        ylabel="substrate diffusivity D_u",
        colorbar_label=r"$\partial Pe_r/\partial L$",
        filepath=path,
        cmap="cubehelix",
    )
    files.append(path)

    # Order/disorder mask at Pe_r ~ 1 boundary.
    mask = (Pe_L_Du >= 1.0).astype(float)
    path = output_dir / "09_order_disorder_mask_L_vs_Du.png"
    save_heatmap(
        mask, L, Du,
        title=r"Reduced-model order/disorder mask using $Pe_r = 1$",
        xlabel="inter-spot spacing L",
        ylabel="substrate diffusivity D_u",
        colorbar_label="1 = disorder side",
        filepath=path,
        cmap="gray",
        vmin=0.0,
        vmax=1.0,
    )
    files.append(path)

    # Communication time itself, to show the emergent quantity's origin.
    t_comm = (L1 ** 2) / Du1
    path = output_dir / "10_communication_time_L_vs_Du.png"
    save_heatmap(
        t_comm, L, Du,
        title=r"Diffusive communication time $t_{comm} \sim L^2 / D_u$",
        xlabel="inter-spot spacing L",
        ylabel="substrate diffusivity D_u",
        colorbar_label="t_comm",
        filepath=path,
        cmap="Blues",
    )
    files.append(path)

    return files


def build_simulation_figures(
    output_dir: Path,
    *,
    n: int,
    steps: int,
    dt: float,
    sample_every: int,
    seed: int,
) -> list[Path]:
    files: list[Path] = []

    # A Pearson-like parameter set, varied only in D_u.
    F = 0.022
    k = 0.051
    Dv = 0.08
    Du_values = np.array([0.14, 0.16, 0.18, 0.20], dtype=np.float64)

    results = {}
    for Du in Du_values:
        results[float(Du)] = simulate_gray_scott(
            float(Du), Dv, F, k,
            n=n,
            steps=steps,
            dt=dt,
            sample_every=sample_every,
            seed=seed,
        )

    times = results[float(Du_values[0])]["times"]
    entropy_map = np.vstack([results[float(Du)]["entropy"] for Du in Du_values])
    gradient_map = np.vstack([results[float(Du)]["gradient_energy"] for Du in Du_values])
    area_map = np.vstack([results[float(Du)]["active_area"] for Du in Du_values])

    path = output_dir / "11_entropy_time_vs_Du.png"
    save_heatmap(
        entropy_map, times, Du_values,
        title="Illustrative Gray–Scott simulation: spatial entropy over time",
        xlabel="time",
        ylabel="substrate diffusivity D_u",
        colorbar_label="entropy",
        filepath=path,
        cmap="viridis",
    )
    files.append(path)

    path = output_dir / "12_gradient_energy_time_vs_Du.png"
    save_heatmap(
        gradient_map, times, Du_values,
        title="Illustrative Gray–Scott simulation: gradient energy over time",
        xlabel="time",
        ylabel="substrate diffusivity D_u",
        colorbar_label="gradient energy",
        filepath=path,
        cmap="plasma",
    )
    files.append(path)

    path = output_dir / "13_active_area_time_vs_Du.png"
    save_heatmap(
        area_map, times, Du_values,
        title="Illustrative Gray–Scott simulation: active-area fraction over time",
        xlabel="time",
        ylabel="substrate diffusivity D_u",
        colorbar_label="active area fraction",
        filepath=path,
        cmap="cividis",
    )
    files.append(path)

    for Du in Du_values:
        result = results[float(Du)]
        du_tag = f"{Du:.2f}".replace(".", "p")

        path_v = output_dir / f"14_activator_v_final_Du_{du_tag}.png"
        save_field_image(
            result["v_final"],
            title=f"Final activator field v at fixed F, k and D_u = {Du:.2f}",
            filepath=path_v,
            cmap="magma",
            colorbar_label="v",
        )
        files.append(path_v)

        path_u = output_dir / f"15_substrate_u_final_Du_{du_tag}.png"
        save_field_image(
            result["u_final"],
            title=f"Final substrate field u at fixed F, k and D_u = {Du:.2f}",
            filepath=path_u,
            cmap="viridis",
            colorbar_label="u",
        )
        files.append(path_u)

    return files


# ---------------------------------------------------------------------------
# Section 6. Report printer
# ---------------------------------------------------------------------------

def print_report(output_dir: Path, generated_files: list[Path]) -> None:
    print("=" * 78)
    print("GREEN PAPER: REPLICATION–COMMUNICATION COMPETITION IN THE GRAY–SCOTT SYSTEM")
    print("=" * 78)
    print(NARRATIVE.strip())
    print()
    print("What was generated")
    print("------------------")
    for path in generated_files:
        print(f"- {path.name}")
    print()
    print("How to read the figures")
    print("-----------------------")
    print("01-10  : reduced-model figures showing why Pe_r is the emergent quantity")
    print("11-13  : simulation heatmaps at fixed reaction kinetics while varying D_u only")
    print("14-15+ : final 2D activator and substrate fields for each D_u")
    print()
    print("Expected qualitative takeaway")
    print("-----------------------------")
    print("If the hypothesis is useful, raising D_u alone should shift the pattern")
    print("toward greater communication, lower Pe_r, lower uncoordinated-birth risk,")
    print("and visibly different spatial organization in the simulation figures.")
    print()
    print(f"Output directory: {output_dir.resolve()}")
    print("=" * 78)


# ---------------------------------------------------------------------------
# Section 7. Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Green paper for the Replication Péclet hypothesis in the Gray–Scott system."
    )
    parser.add_argument(
        "--output-dir",
        default="green_paper_outputs",
        help="Directory where figures will be written.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use a lighter simulation setup.",
    )
    parser.add_argument(
        "--skip-sim",
        action="store_true",
        help="Generate reduced-model figures only.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.quick:
        n = 96
        steps = 1800
        dt = 1.0
        sample_every = 30
    else:
        n = 128
        steps = 2800
        dt = 1.0
        sample_every = 40

    seed = 7

    generated_files = []
    generated_files.extend(build_reduced_model_figures(output_dir))

    if not args.skip_sim:
        generated_files.extend(
            build_simulation_figures(
                output_dir,
                n=n,
                steps=steps,
                dt=dt,
                sample_every=sample_every,
                seed=seed,
            )
        )

    print_report(output_dir, generated_files)


if __name__ == "__main__":
    main()
