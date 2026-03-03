#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_meshes_v3.py — setup_3 mesh generator
Produces a strong-distortion family for revised-hypothesis validation.
"""

import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from pathlib import Path

N_POINTS_BASE = 8500
SEED = 42
TARGET_THETA_DEGS = [10, 30, 50, 60, 70, 80]
THETA_CRIT_DEG = 85.0
TARGET_ORDER = 2.0

def save_vtk(filename, points, simplices, z, theta):
    n_points = len(points)
    n_cells = len(simplices)
    with open(filename, 'w') as f:
        f.write("# vtk DataFile Version 2.0\nz-phase-transition mesh\nASCII\nDATASET UNSTRUCTURED_GRID\n\n")
        f.write(f"POINTS {n_points} float\n")
        for p in points:
            f.write(f"{p[0]:.8e} {p[1]:.8e} 0.0\n")
        f.write(f"\nCELLS {n_cells} {n_cells*4}\n")
        for s in simplices:
            f.write(f"3 {s[0]} {s[1]} {s[2]}\n")
        f.write(f"\nCELL_TYPES {n_cells}\n")
        for _ in range(n_cells):
            f.write("5\n")
        f.write(f"\nCELL_DATA {n_cells}\n")
        f.write("SCALARS z float 1\nLOOKUP_TABLE default\n")
        for val in z:
            f.write(f"{val:.8e}\n")
        f.write("\nSCALARS theta_skew_deg float 1\nLOOKUP_TABLE default\n")
        for val in theta:
            f.write(f"{val:.8e}\n")

def compute_non_ortho_and_z(points, tri):
    simplices = tri.simplices
    n_cells = len(simplices)
    cell_centers = points[simplices].mean(axis=1)

    edge_to_cells = {}
    for icell, verts in enumerate(simplices):
        for i in range(3):
            a, b = sorted([verts[i], verts[(i+1)%3]])
            edge = (a, b)
            if edge not in edge_to_cells:
                edge_to_cells[edge] = []
            edge_to_cells[edge].append(icell)

    theta_max = np.zeros(n_cells)
    for edge, cells in edge_to_cells.items():
        if len(cells) != 2: continue
        c1, c2 = sorted(cells)
        C1, C2 = cell_centers[c1], cell_centers[c2]
        vec_C = C2 - C1
        A, B = points[edge[0]], points[edge[1]]
        edge_vec = B - A
        normal = np.array([-edge_vec[1], edge_vec[0]])
        normal /= np.linalg.norm(normal) + 1e-12
        cos_alpha = np.abs(np.dot(vec_C, normal)) / (np.linalg.norm(vec_C) + 1e-12)
        alpha_deg = np.arccos(np.clip(cos_alpha, 0.0, 1.0)) * 180.0 / np.pi
        theta_max[c1] = max(theta_max[c1], alpha_deg)
        theta_max[c2] = max(theta_max[c2], alpha_deg)

    theta_skew = np.maximum(theta_max, 0.5)
    z = (THETA_CRIT_DEG / theta_skew) * TARGET_ORDER
    return theta_skew, z

def generate_one_mesh(target_deg, base_dir, idx):
    np.random.seed(SEED + idx * 17)
    nx, ny = 120, 72
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    X, Y = np.meshgrid(x, y)
    points = np.column_stack((X.ravel(), Y.ravel()))

    # Aggressive target-dependent distortion
    shear = 1.8 * (target_deg / 50.0)**2.8
    points[:, 0] += shear * points[:, 1]

    # Region-specific bad zones for high targets
    jitter_scale = 0.22 * (target_deg / 50.0)**3.1
    points += np.random.normal(0, jitter_scale, points.shape)

    # Extra warping clusters for low-z pockets in high-target meshes
    if target_deg >= 60:
        mask = (points[:,0] > 0.4) & (points[:,0] < 0.7) & (points[:,1] > 0.3) & (points[:,1] < 0.7)
        points[mask] += np.random.normal(0, 0.35, (mask.sum(), 2))

    points = np.clip(points, 0.002, 0.998)

    tri = Delaunay(points)
    theta_skew, z = compute_non_ortho_and_z(points, tri)

    p95 = np.percentile(theta_skew, 95)
    p99 = np.percentile(theta_skew, 99)
    high = (z > 6).mean() * 100
    trans = ((z >= 3) & (z <= 6)).mean() * 100
    low = (z < 3).mean() * 100

    print(f"  {target_deg:2d}° → 95th θ={p95:5.1f}° (99th={p99:5.1f}°) | "
          f"high/trans/low = {high:5.1f}/{trans:5.1f}/{low:5.1f}%")

    out_dir = base_dir / f"skew_{target_deg:02d}deg"
    out_dir.mkdir(parents=True, exist_ok=True)

    np.save(out_dir / "points.npy", points)
    np.save(out_dir / "tri.npy", tri.simplices)
    np.save(out_dir / "z.npy", z)
    np.save(out_dir / "theta_skew.npy", theta_skew)

    save_vtk(out_dir / "mesh.vtk", points, tri.simplices, z, theta_skew)

    # Plots
    plot_dir = out_dir / "plots"
    plot_dir.mkdir(exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    ax[0].tripcolor(points[:,0], points[:,1], tri.simplices, z, shading='flat', cmap='viridis')
    ax[0].set_title(f"z-field — target {target_deg}°")
    ax[0].set_aspect('equal')
    ax[1].tripcolor(points[:,0], points[:,1], tri.simplices, theta_skew, shading='flat', cmap='plasma')
    ax[1].set_title(f"θ_skew (deg)")
    ax[1].set_aspect('equal')
    plt.savefig(plot_dir / "z_theta.png", dpi=300, bbox_inches='tight')
    plt.close()

    return out_dir

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir / "meshes_v3"
    base_dir.mkdir(exist_ok=True)

    print("=== Generating STRONG DISTORTION family (v3) ===")
    for i, target in enumerate(TARGET_THETA_DEGS):
        generate_one_mesh(target, base_dir, i)

    print(f"\n✅ v3 meshes ready in {base_dir}")
    print("   Open any mesh.vtk in ParaView — you should now see clear regime differentiation!")
    print("   Next: run the gradient test harness on these.")
