from __future__ import annotations

from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from phasewall_poc.geometry import compute_curvature_sign, gaussian_hill
from phasewall_poc.run_bench import run_benchmark
from phasewall_poc.sim_optimizers import run_optimizer_pair_demo
from phasewall_poc.sim_walkers import run_walker_pair_demo


st.set_page_config(page_title="PhaseWall PoC", page_icon="📉", layout="wide")
st.title("PhaseWall PoC: Gaussian 1σ Phase-Wall")
st.caption(
    "Interactive visual + quantitative proof that the curvature sign flip at 1σ can be used "
    "as a control signal for phase-aware stochastic updates."
)


tab_surface, tab_walkers, tab_opt, tab_report = st.tabs(
    ["Surface", "Walker Arena", "Optimizer Arena", "Evidence Report"]
)


with tab_surface:
    st.subheader("Gaussian Surface and Curvature Regime")
    col1, col2, col3 = st.columns(3)
    sigma = col1.slider("σ", 0.5, 2.0, 1.0, 0.1)
    extent = col2.slider("Grid extent", 1.5, 4.0, 3.0, 0.1)
    grid_n = col3.slider("Grid resolution", 30, 120, 80, 5)

    x = np.linspace(-extent, extent, grid_n)
    y = np.linspace(-extent, extent, grid_n)
    X, Y = np.meshgrid(x, y)
    Z = gaussian_hill(X, Y, sigma=sigma)
    R = np.sqrt(X**2 + Y**2)
    K = compute_curvature_sign(R, sigma=sigma).astype(float)

    fig = go.Figure(
        data=[
            go.Surface(
                x=X,
                y=Y,
                z=Z,
                surfacecolor=K,
                colorscale=[
                    [0.0, "rgb(220,20,60)"],
                    [0.49, "rgb(220,20,60)"],
                    [0.50, "rgb(0,0,0)"],
                    [1.0, "rgb(46,204,113)"],
                ],
                cmin=-1,
                cmax=1,
                showscale=False,
                name="surface",
            )
        ]
    )

    theta = np.linspace(0, 2 * np.pi, 300)
    ring_x = sigma * np.cos(theta)
    ring_y = sigma * np.sin(theta)
    ring_z = gaussian_hill(ring_x, ring_y, sigma=sigma)

    fig.add_trace(
        go.Scatter3d(
            x=ring_x,
            y=ring_y,
            z=ring_z,
            mode="lines",
            line={"color": "white", "width": 8},
            name="1σ ring",
        )
    )
    fig.update_layout(
        height=620,
        margin={"l": 0, "r": 0, "t": 20, "b": 0},
        scene={"xaxis_title": "x", "yaxis_title": "y", "zaxis_title": "f(x,y)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "- Green region: `K > 0` (elliptic, converging regime)  \n"
        "- Black ring: `K = 0` at `r = σ`  \n"
        "- Red region: `K < 0` (hyperbolic, diverging regime)"
    )


with tab_walkers:
    st.subheader("Walker Arena: Vanilla vs Phase-Aware")
    c1, c2, c3, c4 = st.columns(4)
    n_walkers = c1.slider("Walkers", 20, 300, 120, 10)
    steps = c2.slider("Steps", 20, 300, 100, 10)
    noise = c3.slider("Noise std", 0.01, 1.0, 0.25, 0.01)
    strength = c4.slider("PhaseWall strength", 0.0, 1.0, 0.4, 0.05)

    seed = st.number_input("Seed", min_value=0, max_value=1_000_000, value=42, step=1)

    demo = run_walker_pair_demo(
        dim=2,
        n_agents=int(n_walkers),
        steps=int(steps),
        noise_std=float(noise),
        seed=int(seed),
        phasewall_strength=float(strength),
    )

    plot_cols = st.columns(2)
    for idx, method in enumerate(["vanilla", "phasewall"]):
        item = demo[method]
        traj = item["trajectories"]
        final = traj[-1]
        fig2d = go.Figure()
        n_show = min(40, traj.shape[1])
        for i in range(n_show):
            fig2d.add_trace(
                go.Scatter(
                    x=traj[:, i, 0],
                    y=traj[:, i, 1],
                    mode="lines",
                    line={"width": 1},
                    opacity=0.45,
                    showlegend=False,
                )
            )
        fig2d.add_trace(
            go.Scatter(
                x=final[:, 0],
                y=final[:, 1],
                mode="markers",
                marker={"size": 6},
                showlegend=False,
            )
        )
        th = np.linspace(0, 2 * np.pi, 200)
        fig2d.add_trace(
            go.Scatter(
                x=np.cos(th),
                y=np.sin(th),
                mode="lines",
                line={"dash": "dash", "color": "black"},
                showlegend=False,
            )
        )
        fig2d.update_layout(
            title=method,
            xaxis_title="x",
            yaxis_title="y",
            height=450,
            xaxis={"scaleanchor": "y", "scaleratio": 1},
        )
        plot_cols[idx].plotly_chart(fig2d, use_container_width=True)

    metric_cols = st.columns(4)
    metric_cols[0].metric(
        "Escape rate (vanilla)", f"{demo['vanilla']['metrics']['escape_rate']:.3f}"
    )
    metric_cols[1].metric(
        "Escape rate (phasewall)", f"{demo['phasewall']['metrics']['escape_rate']:.3f}"
    )
    metric_cols[2].metric(
        "Angular dispersion Δ",
        f"{demo['phasewall']['metrics']['angular_dispersion'] - demo['vanilla']['metrics']['angular_dispersion']:.3f}",
    )
    metric_cols[3].metric(
        "Inside wall fraction Δ",
        f"{demo['phasewall']['metrics']['inside_fraction'] - demo['vanilla']['metrics']['inside_fraction']:.3f}",
    )


with tab_opt:
    st.subheader("Optimizer Arena: Toy ES + CMA-ES-Style")
    o1, o2, o3, o4, o5 = st.columns(5)
    engine = o1.selectbox("Engine", ["toy_es", "cmaes_style"], index=0)
    objective = o2.selectbox("Objective", ["sphere", "rosenbrock", "rastrigin"], index=0)
    dim = o3.selectbox("Dimension", [2, 10], index=1)
    eval_budget = o4.slider("Eval budget", 100, 4000, 1200, 100)
    seeds = o5.slider("Seeds", 3, 30, 10, 1)

    on1, on2, on3 = st.columns(3)
    pop_size = on1.slider("Population", 6, 80, 24, 2)
    obs_noise = on2.slider("Objective noise std", 0.0, 1.0, 0.1, 0.01)
    pw_strength = on3.slider("PhaseWall strength (opt)", 0.0, 1.0, 0.4, 0.05)

    opt_demo = run_optimizer_pair_demo(
        engine=engine,
        objective=objective,
        dim=int(dim),
        eval_budget=int(eval_budget),
        population_size=int(pop_size),
        noise_std=float(obs_noise),
        n_seeds=int(seeds),
        phasewall_strength=float(pw_strength),
    )

    curve = go.Figure()
    curve.add_trace(
        go.Scatter(
            x=opt_demo["vanilla"]["median_history_x"],
            y=opt_demo["vanilla"]["median_history_y"],
            mode="lines",
            name="vanilla",
        )
    )
    curve.add_trace(
        go.Scatter(
            x=opt_demo["phasewall"]["median_history_x"],
            y=opt_demo["phasewall"]["median_history_y"],
            mode="lines",
            name="phasewall",
        )
    )
    curve.update_layout(height=450, xaxis_title="Evaluations", yaxis_title="Best-so-far")
    st.plotly_chart(curve, use_container_width=True)

    mcols = st.columns(4)
    mcols[0].metric("Vanilla median final", f"{opt_demo['vanilla']['median_final']:.5g}")
    mcols[1].metric("PhaseWall median final", f"{opt_demo['phasewall']['median_final']:.5g}")
    mcols[2].metric("Win-rate", f"{opt_demo['win_rate']:.3f}")
    mcols[3].metric("Median ratio", f"{opt_demo['median_ratio']:.3f}")


with tab_report:
    st.subheader("Evidence Report Export")
    r1, r2, r3 = st.columns(3)
    preset = r1.selectbox("Preset", ["core"], index=0)
    seed_count = r2.number_input("Seeds", min_value=1, max_value=100, value=20, step=1)
    out = r3.text_input("Output dir", value="artifacts/latest")

    if st.button("Run benchmark and export artifacts", type="primary"):
        with st.spinner("Running benchmark suite..."):
            results, aggs, out_dir = run_benchmark(
                preset=preset,
                seed_count=int(seed_count),
                out_dir=Path(out),
            )

        st.success(f"Artifacts written to: {out_dir}")
        st.dataframe(
            {
                "scenario": [a.scenario for a in aggs],
                "engine": [a.engine for a in aggs],
                "method": [a.method for a in aggs],
                "median_score": [a.median_score for a in aggs],
                "win_rate": [a.win_rate for a in aggs],
                "ratio_vs_vanilla": [a.ratio_vs_vanilla for a in aggs],
                "wilcoxon_p": [a.wilcoxon_p for a in aggs],
            }
        )

        st.markdown("### File outputs")
        st.code(
            "\n".join(
                [
                    str(out_dir / "results.csv"),
                    str(out_dir / "summary.md"),
                    str(out_dir / "fig_score_bars.png"),
                    str(out_dir / "fig_win_rate.png"),
                ]
            )
        )
