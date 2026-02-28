import argparse
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.patches import FancyArrowPatch


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    default_output = project_root / "figures" / "em-gw-priming-timeline.png"
    parser = argparse.ArgumentParser(description="Generate EM-GW priming timeline figure.")
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help="Output image path (default: em-gw-priming-window/figures/em-gw-priming-timeline.png).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the figure interactively after saving.",
    )
    return parser.parse_args()


def build_figure():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(-1, 25)
    ax.set_ylim(0, 10)
    ax.set_xlabel("Hours after solar EM event (flare or HSS onset)", fontsize=14)
    ax.set_ylabel("Relative amplitude / state", fontsize=14)
    ax.set_title(
        "EM-GW Priming Window Mechanism\nIonospheric Conductivity Memory Gates Tropospheric Gravity Waves",
        fontsize=16,
        pad=20,
    )

    # Time axis
    ax.axhline(y=5, xmin=0.05, xmax=0.95, color="black", linewidth=2, alpha=0.7)

    # Solar EM event
    ax.plot(0, 5, "o", color="red", markersize=12)
    ax.annotate(
        "Solar EM event\n(flare / HSS onset)",
        xy=(0, 5.5),
        xytext=(0.5, 7.5),
        arrowprops=dict(arrowstyle="->", color="red"),
        fontsize=11,
        ha="center",
    )

    # Conductivity decay curve
    t = np.linspace(0, 24, 500)
    r_sigma = 1 + 3.0 * np.exp(-t / 5.0)
    ax.plot(t, r_sigma + 1.5, "b-", linewidth=3.5, label="Conductivity enhancement r_sigma(t) (one-way memory)")

    # Priming window shading (3-10 h)
    ax.fill_between(
        t,
        1,
        8,
        where=(t >= 3) & (t <= 10),
        color="lightblue",
        alpha=0.35,
        label="Priming window (3-10 h)",
    )

    # GW arrivals
    ax.plot(5, 1.5, "s", color="green", markersize=10)
    ax.annotate(
        "Tropospheric GW packet\narrives at 5 h (inside window)",
        xy=(5, 1.5),
        xytext=(5.5, 0.5),
        arrowprops=dict(arrowstyle="->", color="green"),
        fontsize=11,
    )

    ax.plot(14, 1.5, "s", color="orange", markersize=10)
    ax.annotate(
        "Same GW packet\narrives at 14 h (quiescent)",
        xy=(14, 1.5),
        xytext=(14.5, 0.5),
        arrowprops=dict(arrowstyle="->", color="orange"),
        fontsize=11,
    )

    # Amplified vs baseline responses
    ax.add_patch(
        FancyArrowPatch(
            (5, 3),
            (5, 7),
            connectionstyle="arc3,rad=0.3",
            color="darkgreen",
            linewidth=3,
            arrowstyle="->",
            mutation_scale=20,
        )
    )
    ax.text(6.5, 5, "2-4x amplified response\n(DeltaTEC, Deltaf1, sharp TIDs)", fontsize=12, color="darkgreen")

    ax.add_patch(
        FancyArrowPatch(
            (14, 3),
            (14, 5.5),
            connectionstyle="arc3,rad=0.2",
            color="darkorange",
            linewidth=2,
            arrowstyle="->",
            mutation_scale=15,
        )
    )
    ax.text(15.5, 4.2, "Baseline response", fontsize=11, color="darkorange")

    # Key concept boxes
    ax.text(
        1.5,
        8.5,
        "Fast EM writes conductivity memory\n(no reverse feedback)",
        fontsize=12,
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )
    ax.text(
        18,
        8,
        "Slow GW from below reads the gate",
        fontsize=12,
        bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.8),
    )

    ax.legend(loc="upper right", fontsize=11)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig, plt


def main() -> None:
    args = parse_args()
    if not args.show:
        matplotlib.use("Agg")
    fig, plt = build_figure()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    if args.show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
