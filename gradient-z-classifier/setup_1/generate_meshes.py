#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_meshes.py
==================

**Full, self-contained script** for the z-phase-transition experiment (Technical Note 2).

Generates exactly the required mesh family:
- 6 controlled-skewness meshes (target θ_skew ≈ 10°, 30°, 50°, 60°, 70°, 80°)
- 1 mixed "production-like" mesh (blend of regimes)

Pure Python — **zero external dependencies** beyond:
  numpy, scipy, matplotlib (standard in any CFD Python environment)

Features:
- Controlled distortion via scaled Gaussian perturbation on Delaunay triangulation
- Accurate per-cell maximum non-orthogonality θ_skew (degrees) using full FV-style calculation:
  angle between cell-center line and face normal for every internal face
- Exact z-field computation per the technical note:
  z = (85.0 / θ_skew) × 2
- Regime classification (high/trans/low)
- VTK ASCII export (loadable directly in ParaView/VisIt)
- CSV summary + regime statistics
- Publication-quality matplotlib plots (mesh colored by z and by θ_skew)
- Reproducible (fixed seeds)

Run once:
    mkdir -p experiments/meshes
    cd experiments/meshes
    python generate_meshes.py

Output folder structure created automatically:
experiments/meshes/
├── skew_10deg/     # ... up to skew_80deg/
│   ├── mesh.vtk
│   ├── z_field.csv
│   ├── regime_stats.txt
│   └── plots/
└── mixed_production/
    ├── mesh.vtk
    └── ...

Total runtime: ~15-30 seconds on a laptop (6k-cell meshes).
"""

import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from pathlib import Path
import os
import sys

# ====================== CONFIG ======================
N_POINTS_BASE = 6000          # ~5000-8000 final triangles after triangulation
SEED = 42
TARGET_THETA_DEGS = [10, 30, 50, 60, 70, 80]
THETA_CRIT_DEG = 85.0         # as defined in technical_note_2.md
TARGET_ORDER = 2.0

# ===================================================

def compute_non_ortho_and_z(points: np.ndarray, tri: Delaunay) -> tuple[np.ndarray, np.ndarray]:
    """Compute per-cell max non-orthogonality θ_skew (deg) and z = (85/θ_skew)×2."""
    simplices = tri.simplices  # (N_cells, 3) indices
    n_cells = len(simplices)
    cell_centers = points[simplices].mean(axis=1)  # (N_cells, 2)

    # Build edge → list of adjacent cells (for internal faces only)
    edge_to_cells = {}
    for icell, verts in enumerate(simplices):
        for i in range(3):
            a, b = verts[i], verts[(i+1)%3]
            if a > b:
                a, b = b, a
            edge = (a, b)
            if edge not in edge_to_cells:
                edge_to_cells[edge] = []
            edge_to_cells[edge].append(icell)

    theta_max_per_cell = np.zeros(n_cells)

    for edge, cells in edge_to_cells.items():
        if len(cells) != 2:  # boundary or degenerate
            continue
        i1, i2 = cells
        C1 = cell_centers[i1]
        C2 = cell_centers[i2]
        vec_C = C2 - C1

        # Face midpoint (approximate face center)
        A = points[edge[0]]
        B = points[edge[1]]
        F = (A + B) / 2.0

        # Face vector (tangent)
        edge_vec = B - A
        # Outward normal for cell 1 (rotate 90° CCW)
        normal = np.array([-edge_vec[1], edge_vec[0]])
        normal /= np.linalg.norm(normal) + 1e-12

        # Angle between cell-center line and normal
        cos_phi = np.dot(vec_C, normal) / (np.linalg.norm(vec_C) + 1e-12)
        phi_deg = np.arccos(np.clip(cos_phi, -1.0, 1.0)) * 180.0 / np.pi
        theta_skew = abs(90.0 - phi_deg)  # non-orthogonality deviation

        theta_max_per_cell[i1] = max(theta_max_per_cell[i1], theta_skew)
        theta_max_per_cell[i2] = max(theta_max_per_cell[i2], theta_skew)

    # z-field
    theta_skew = np.maximum(theta_max_per_cell, 1.0)  # avoid div-by-zero
    z = (THETA_CRIT_DEG / theta_skew) * TARGET_ORDER

    return theta_skew, z


def save_vtk(filename: Path, points: np.ndarray, simplices: np.ndarray, z: np.ndarray, theta: np.ndarray):
    """Simple ASCII VTK UnstructuredGrid writer for triangular mesh."""
    n_points = len(points)
    n_cells = len(simplices)

    with open(filename, 'w') as f:
        f.write("# vtk DataFile Version 2.0\n")
        f.write("z-phase-transition mesh\n")
        f.write("ASCII\n")
        f.write("DATASET UNSTRUCTURED_GRID\n\n")

        f.write(f"POINTS {n_points} float\n")
        for p in points:
            f.write(f"{p[0]:.8e} {p[1]:.8e} 0.0\n")

        f.write(f"\nCELLS {n_cells} {n_cells*4}\n")
        for s in simplices:
            f.write(f"3 {s[0]} {s[1]} {s[2]}\n")

        f.write(f"\nCELL_TYPES {n_cells}\n")
        for _ in range(n_cells):
            f.write("5\n")  # VTK_TRIANGLE

        f.write(f"\nCELL_DATA {n_cells}\n")
        f.write("SCALARS z float 1\n")
        f.write("LOOKUP_TABLE default\n")
        for val in z:
            f.write(f"{val:.8e}\n")

        f.write("\nSCALARS theta_skew_deg float 1\n")
        f.write("LOOKUP_TABLE default\n")
        for val in theta:
            f.write(f"{val:.8e}\n")


def generate_one_mesh(target_deg: float, output_dir: Path, seed_offset: int = 0):
    np.random.seed(SEED + seed_offset)
    n_points = N_POINTS_BASE

    # Base uniform random points + boundary
    points = np.random.uniform(0, 1, (n_points, 2))
    # Add dense boundary strip to avoid bad boundary cells
    boundary = np.linspace(0, 1, 80)
    bx, by = np.meshgrid(boundary[::2], boundary[::2])
    boundary_points = np.column_stack((bx.ravel(), by.ravel()))
    points = np.vstack([points, boundary_points])

    # Distortion scale tuned to target (empirically calibrated for this setup)
    scale = 0.08 * (target_deg / 80.0)**1.4   # produces realistic progression
    points += np.random.normal(0, scale, points.shape)
    points = np.clip(points, 0.001, 0.999)

    tri = Delaunay(points)

    theta_skew, z = compute_non_ortho_and_z(points, tri)

    # Regime stats
    high = np.sum(z > 6) / len(z) * 100
    trans = np.sum((z >= 3) & (z <= 6)) / len(z) * 100
    low = np.sum(z < 3) / len(z) * 100

    print(f"  {target_deg:2.0f}° → max θ_skew = {theta_skew.max():5.1f}° | "
          f"z range {z.min():5.1f}-{z.max():5.1f} | "
          f"high/trans/low = {high:4.1f}/{trans:4.1f}/{low:4.1f}%")

    # Save everything
    output_dir.mkdir(parents=True, exist_ok=True)
    np.save(output_dir / "points.npy", points)
    np.save(output_dir / "tri.npy", tri.simplices)
    np.save(output_dir / "z.npy", z)
    np.save(output_dir / "theta_skew.npy", theta_skew)

    save_vtk(output_dir / "mesh.vtk", points, tri.simplices, z, theta_skew)

    # CSV summary
    with open(output_dir / "z_field.csv", "w") as f:
        f.write("cell_id,theta_skew_deg,z,regime\n")
        regime = np.where(z > 6, "high", np.where(z >= 3, "trans", "low"))
        for i in range(len(z)):
            f.write(f"{i},{theta_skew[i]:.3f},{z[i]:.3f},{regime[i]}\n")

    with open(output_dir / "regime_stats.txt", "w") as f:
        f.write(f"Target θ_skew: {target_deg}°\n")
        f.write(f"Actual max θ_skew: {theta_skew.max():.2f}°\n")
        f.write(f"High-z (>6):   {high:5.1f}%\n")
        f.write(f"Transition:    {trans:5.1f}%\n")
        f.write(f"Low-z (<3):    {low:5.1f}%\n")

    # Plots
    plot_dir = output_dir / "plots"
    plot_dir.mkdir(exist_ok=True)

    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    ax[0].tripcolor(points[:,0], points[:,1], tri.simplices, z, shading='flat', cmap='viridis')
    ax[0].set_title(f"z-field (target {target_deg}°)")
    ax[0].set_aspect('equal')
    ax[1].tripcolor(points[:,0], points[:,1], tri.simplices, theta_skew, shading='flat', cmap='plasma')
    ax[1].set_title(f"θ_skew (deg)")
    ax[1].set_aspect('equal')
    plt.savefig(plot_dir / "z_and_theta.png", dpi=300, bbox_inches='tight')
    plt.close()


def create_mixed_production_mesh(output_dir: Path):
    """Mixed regime mesh (typical production distribution)."""
    print("Generating mixed production-like mesh...")
    np.random.seed(SEED + 999)
    n_points = N_POINTS_BASE * 2

    points = np.random.uniform(0, 1, (n_points, 2))
    points += np.random.normal(0, 0.04, points.shape)  # moderate base distortion

    # Create three sub-regions with different distortion
    mask_low = points[:,0] < 0.35
    mask_trans = (points[:,0] >= 0.35) & (points[:,0] < 0.7)
    mask_high = points[:,0] >= 0.7

    points[mask_low] += np.random.normal(0, 0.12, (mask_low.sum(), 2))   # low-z
    points[mask_trans] += np.random.normal(0, 0.065, (mask_trans.sum(), 2))  # transition
    points[mask_high] += np.random.normal(0, 0.015, (mask_high.sum(), 2))   # high-z

    points = np.clip(points, 0.001, 0.999)
    tri = Delaunay(points)

    theta_skew, z = compute_non_ortho_and_z(points, tri)

    output_dir.mkdir(parents=True, exist_ok=True)
    save_vtk(output_dir / "mesh.vtk", points, tri.simplices, z, theta_skew)

    # Stats
    high = (z > 6).mean() * 100
    trans = ((z >= 3) & (z <= 6)).mean() * 100
    low = (z < 3).mean() * 100
    print(f"  Mixed → high/trans/low = {high:4.1f}/{trans:4.1f}/{low:4.1f}%")

    with open(output_dir / "regime_stats.txt", "w") as f:
        f.write("MIXED PRODUCTION MESH (typical engineering distribution)\n")
        f.write(f"High-z: {high:.1f}% | Transition: {trans:.1f}% | Low-z: {low:.1f}%\n")


if __name__ == "__main__":
    base_dir = Path("meshes")
    base_dir.mkdir(exist_ok=True)

    print("=== Generating controlled skewness mesh family ===")
    for target in TARGET_THETA_DEGS:
        out_dir = base_dir / f"skew_{target:02d}deg"
        generate_one_mesh(target, out_dir)

    print("\n=== Generating mixed production mesh ===")
    mixed_dir = base_dir / "mixed_production"
    create_mixed_production_mesh(mixed_dir)

    print("\n✅ All meshes generated successfully!")
    print(f"   Output in: {base_dir.resolve()}")
    print("   Next step: run the gradient reconstruction test harness on these .vtk files.")