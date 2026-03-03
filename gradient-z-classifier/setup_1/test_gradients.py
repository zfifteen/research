#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manufactured-solution gradient reconstruction harness for setup_1.

Runs GG, WLSQ, and GLSQ (alpha in {0.0, 0.5, 1.0}) across discovered meshes,
produces comparison tables, plots, CSVs, and a markdown validation report.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


EPS = 1.0e-12
THETA_CRIT_DEG = 85.0
TARGET_ORDER = 2.0
GLSQ_ALPHAS = (0.0, 0.5, 1.0)
VALID_SCHEMES = ("gg", "wlsq", "glsq")
_MESH_CACHE: dict[Path, "MeshData"] = {}


@dataclass
class MeshData:
    folder: Path
    name: str
    points: np.ndarray
    tri: np.ndarray
    z: np.ndarray
    theta_skew: np.ndarray
    centers: np.ndarray
    areas: np.ndarray
    neighbors: list[np.ndarray]
    directed_i: np.ndarray
    directed_j: np.ndarray
    internal_i: np.ndarray
    internal_j: np.ndarray
    internal_fc: np.ndarray
    internal_si: np.ndarray
    internal_sj: np.ndarray
    internal_edge_vertices: np.ndarray
    boundary_i: np.ndarray
    boundary_fc: np.ndarray
    boundary_si: np.ndarray
    boundary_edge_vertices: np.ndarray
    target_theta: float | None


def _parse_target_theta(name: str) -> float | None:
    match = re.search(r"skew_(\d+)deg", name)
    if not match:
        return None
    return float(match.group(1))


def _find_line_index(lines: list[str], startswith: str, start: int = 0) -> int:
    for i in range(start, len(lines)):
        if lines[i].strip().startswith(startswith):
            return i
    return -1


def _collect_numbers(lines: list[str], start: int, count: int, dtype: Any) -> tuple[np.ndarray, int]:
    vals: list[Any] = []
    idx = start
    while len(vals) < count and idx < len(lines):
        stripped = lines[idx].strip()
        if stripped:
            vals.extend(stripped.split())
        idx += 1
    if len(vals) < count:
        raise ValueError(f"Could not collect {count} numeric entries from VTK.")
    arr = np.asarray(vals[:count], dtype=dtype)
    return arr, idx


def _read_scalar_from_vtk(lines: list[str], scalar_name: str, n_cells: int) -> np.ndarray | None:
    scalar_idx = _find_line_index(lines, f"SCALARS {scalar_name} ")
    if scalar_idx < 0:
        return None
    lookup_idx = _find_line_index(lines, "LOOKUP_TABLE", scalar_idx + 1)
    if lookup_idx < 0:
        return None
    vals, _ = _collect_numbers(lines, lookup_idx + 1, n_cells, float)
    return vals


def _read_ascii_vtk(vtk_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None]:
    lines = vtk_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    points_idx = _find_line_index(lines, "POINTS ")
    if points_idx < 0:
        raise ValueError(f"POINTS section not found in {vtk_path}")
    n_points = int(lines[points_idx].split()[1])
    point_vals, after_points = _collect_numbers(lines, points_idx + 1, n_points * 3, float)
    points = point_vals.reshape(n_points, 3)[:, :2]

    cells_idx = _find_line_index(lines, "CELLS ", after_points)
    if cells_idx < 0:
        raise ValueError(f"CELLS section not found in {vtk_path}")
    cells_tokens = lines[cells_idx].split()
    n_cells = int(cells_tokens[1])
    cells_total = int(cells_tokens[2])
    cell_vals, _ = _collect_numbers(lines, cells_idx + 1, cells_total, int)
    tri = np.empty((n_cells, 3), dtype=np.int64)
    cursor = 0
    for i in range(n_cells):
        nverts = int(cell_vals[cursor])
        cursor += 1
        if nverts != 3:
            raise ValueError(f"Only triangular cells are supported, got {nverts} in {vtk_path}")
        tri[i, :] = cell_vals[cursor : cursor + 3]
        cursor += 3

    z_vals = _read_scalar_from_vtk(lines, "z", n_cells)
    theta_vals = _read_scalar_from_vtk(lines, "theta_skew_deg", n_cells)
    return points, tri, z_vals, theta_vals


def _oriented_face_vector(pa: np.ndarray, pb: np.ndarray, face_center: np.ndarray, cell_center: np.ndarray) -> np.ndarray:
    tangential = pb - pa
    normal = np.array([tangential[1], -tangential[0]], dtype=float)
    if np.dot(normal, face_center - cell_center) < 0.0:
        normal *= -1.0
    return normal


def _compute_theta_and_z(mesh: MeshData) -> tuple[np.ndarray, np.ndarray]:
    theta_max = np.zeros(mesh.tri.shape[0], dtype=float)
    if mesh.internal_i.size > 0:
        i = mesh.internal_i
        j = mesh.internal_j
        dvec = mesh.centers[j] - mesh.centers[i]
        normals = mesh.internal_si
        nrm = np.linalg.norm(normals, axis=1)
        dnm = np.linalg.norm(dvec, axis=1)
        cos_alpha = np.abs(np.sum(dvec * normals, axis=1)) / np.maximum(dnm * nrm, EPS)
        alpha_deg = np.degrees(np.arccos(np.clip(cos_alpha, 0.0, 1.0)))
        np.maximum.at(theta_max, i, alpha_deg)
        np.maximum.at(theta_max, j, alpha_deg)
    theta_skew = np.maximum(theta_max, 0.5)
    z = (THETA_CRIT_DEG / theta_skew) * TARGET_ORDER
    return theta_skew, z


def _build_mesh_data(folder: Path, points: np.ndarray, tri: np.ndarray, z: np.ndarray | None, theta: np.ndarray | None) -> MeshData:
    tri = np.asarray(tri, dtype=np.int64)
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] < 2:
        raise ValueError(f"Invalid points array shape: {points.shape}")
    points = points[:, :2]

    a = points[tri[:, 0]]
    b = points[tri[:, 1]]
    c = points[tri[:, 2]]
    centers = (a + b + c) / 3.0
    areas = 0.5 * np.abs((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0]))
    areas = np.maximum(areas, EPS)

    edge_map: dict[tuple[int, int], list[tuple[int, int, int]]] = {}
    for cell_idx, verts in enumerate(tri):
        for k in range(3):
            v0 = int(verts[k])
            v1 = int(verts[(k + 1) % 3])
            key = (v0, v1) if v0 < v1 else (v1, v0)
            edge_map.setdefault(key, []).append((cell_idx, v0, v1))

    n_cells = tri.shape[0]
    neighbors_set = [set() for _ in range(n_cells)]
    directed_i_list: list[int] = []
    directed_j_list: list[int] = []

    internal_i_list: list[int] = []
    internal_j_list: list[int] = []
    internal_fc_list: list[np.ndarray] = []
    internal_si_list: list[np.ndarray] = []
    internal_sj_list: list[np.ndarray] = []
    internal_edges: list[tuple[int, int]] = []

    boundary_i_list: list[int] = []
    boundary_fc_list: list[np.ndarray] = []
    boundary_si_list: list[np.ndarray] = []
    boundary_edges: list[tuple[int, int]] = []

    for edge_key, entries in edge_map.items():
        p0 = points[edge_key[0]]
        p1 = points[edge_key[1]]
        face_center = 0.5 * (p0 + p1)
        if len(entries) == 2:
            (ci, a0, b0), (cj, a1, b1) = entries
            si = _oriented_face_vector(points[a0], points[b0], face_center, centers[ci])
            sj = _oriented_face_vector(points[a1], points[b1], face_center, centers[cj])
            internal_i_list.append(ci)
            internal_j_list.append(cj)
            internal_fc_list.append(face_center)
            internal_si_list.append(si)
            internal_sj_list.append(sj)
            internal_edges.append(edge_key)
            neighbors_set[ci].add(cj)
            neighbors_set[cj].add(ci)
            directed_i_list.extend((ci, cj))
            directed_j_list.extend((cj, ci))
        elif len(entries) == 1:
            ci, a0, b0 = entries[0]
            si = _oriented_face_vector(points[a0], points[b0], face_center, centers[ci])
            boundary_i_list.append(ci)
            boundary_fc_list.append(face_center)
            boundary_si_list.append(si)
            boundary_edges.append(edge_key)

    neighbors = [np.asarray(sorted(v), dtype=np.int64) if v else np.empty(0, dtype=np.int64) for v in neighbors_set]

    mesh = MeshData(
        folder=folder,
        name=folder.name,
        points=points,
        tri=tri,
        z=np.asarray(z, dtype=float) if z is not None else np.empty(n_cells, dtype=float),
        theta_skew=np.asarray(theta, dtype=float) if theta is not None else np.empty(n_cells, dtype=float),
        centers=centers,
        areas=areas,
        neighbors=neighbors,
        directed_i=np.asarray(directed_i_list, dtype=np.int64),
        directed_j=np.asarray(directed_j_list, dtype=np.int64),
        internal_i=np.asarray(internal_i_list, dtype=np.int64),
        internal_j=np.asarray(internal_j_list, dtype=np.int64),
        internal_fc=np.asarray(internal_fc_list, dtype=float).reshape(-1, 2),
        internal_si=np.asarray(internal_si_list, dtype=float).reshape(-1, 2),
        internal_sj=np.asarray(internal_sj_list, dtype=float).reshape(-1, 2),
        internal_edge_vertices=np.asarray(internal_edges, dtype=np.int64).reshape(-1, 2),
        boundary_i=np.asarray(boundary_i_list, dtype=np.int64),
        boundary_fc=np.asarray(boundary_fc_list, dtype=float).reshape(-1, 2),
        boundary_si=np.asarray(boundary_si_list, dtype=float).reshape(-1, 2),
        boundary_edge_vertices=np.asarray(boundary_edges, dtype=np.int64).reshape(-1, 2),
        target_theta=_parse_target_theta(folder.name),
    )

    if mesh.z.size != n_cells or mesh.theta_skew.size != n_cells:
        theta_new, z_new = _compute_theta_and_z(mesh)
        mesh.theta_skew = theta_new
        mesh.z = z_new
    return mesh


def load_mesh(folder: str | Path) -> MeshData:
    mesh_folder = Path(folder).resolve()
    if mesh_folder in _MESH_CACHE:
        return _MESH_CACHE[mesh_folder]

    npy_points = mesh_folder / "points.npy"
    npy_tri = mesh_folder / "tri.npy"
    npy_z = mesh_folder / "z.npy"
    npy_theta = mesh_folder / "theta_skew.npy"
    vtk_file = mesh_folder / "mesh.vtk"

    points: np.ndarray
    tri: np.ndarray
    z_vals: np.ndarray | None = None
    theta_vals: np.ndarray | None = None

    if npy_points.exists() and npy_tri.exists():
        points = np.load(npy_points)
        tri = np.load(npy_tri)
        if npy_z.exists():
            z_vals = np.load(npy_z)
        if npy_theta.exists():
            theta_vals = np.load(npy_theta)
        if (z_vals is None or theta_vals is None) and vtk_file.exists():
            _, _, z_vtk, theta_vtk = _read_ascii_vtk(vtk_file)
            z_vals = z_vals if z_vals is not None else z_vtk
            theta_vals = theta_vals if theta_vals is not None else theta_vtk
    elif vtk_file.exists():
        points, tri, z_vals, theta_vals = _read_ascii_vtk(vtk_file)
    else:
        raise FileNotFoundError(f"No mesh found in {mesh_folder}: expected .npy or mesh.vtk")

    mesh = _build_mesh_data(mesh_folder, points, tri, z_vals, theta_vals)
    _MESH_CACHE[mesh_folder] = mesh
    return mesh


def _manufactured_field(points: np.ndarray) -> np.ndarray:
    x = points[:, 0]
    y = points[:, 1]
    return np.sin(np.pi * x) * np.cos(np.pi * y)


def _manufactured_grad(points: np.ndarray) -> np.ndarray:
    x = points[:, 0]
    y = points[:, 1]
    gx = np.pi * np.cos(np.pi * x) * np.cos(np.pi * y)
    gy = -np.pi * np.sin(np.pi * x) * np.sin(np.pi * y)
    return np.column_stack((gx, gy))


def green_gauss_grad(mesh: MeshData, f_cell: np.ndarray, boundary_face_values: np.ndarray | None = None) -> np.ndarray:
    n_cells = mesh.centers.shape[0]
    grad = np.zeros((n_cells, 2), dtype=float)

    if mesh.internal_i.size > 0:
        i = mesh.internal_i
        j = mesh.internal_j
        f_face = 0.5 * (f_cell[i] + f_cell[j])
        np.add.at(grad, i, f_face[:, None] * mesh.internal_si)
        np.add.at(grad, j, f_face[:, None] * mesh.internal_sj)

    if mesh.boundary_i.size > 0:
        if boundary_face_values is None or boundary_face_values.size != mesh.boundary_i.size:
            boundary_face_values = _manufactured_field(mesh.boundary_fc)
        np.add.at(grad, mesh.boundary_i, boundary_face_values[:, None] * mesh.boundary_si)

    grad /= mesh.areas[:, None]
    return grad


def wlsq_grad(mesh: MeshData, f_cell: np.ndarray, regularization: float = 1.0e-14) -> np.ndarray:
    n_cells = mesh.centers.shape[0]
    if mesh.directed_i.size == 0:
        return np.zeros((n_cells, 2), dtype=float)

    i = mesh.directed_i
    j = mesh.directed_j
    d = mesh.centers[j] - mesh.centers[i]
    dx = d[:, 0]
    dy = d[:, 1]
    df = f_cell[j] - f_cell[i]
    w = 1.0 / (dx * dx + dy * dy + EPS)

    a_xx = np.zeros(n_cells, dtype=float)
    a_xy = np.zeros(n_cells, dtype=float)
    a_yy = np.zeros(n_cells, dtype=float)
    b_x = np.zeros(n_cells, dtype=float)
    b_y = np.zeros(n_cells, dtype=float)

    np.add.at(a_xx, i, w * dx * dx)
    np.add.at(a_xy, i, w * dx * dy)
    np.add.at(a_yy, i, w * dy * dy)
    np.add.at(b_x, i, w * dx * df)
    np.add.at(b_y, i, w * dy * df)

    a_xx += regularization
    a_yy += regularization

    det = a_xx * a_yy - a_xy * a_xy
    grad = np.zeros((n_cells, 2), dtype=float)
    good = np.abs(det) > 1.0e-20
    grad[good, 0] = (a_yy[good] * b_x[good] - a_xy[good] * b_y[good]) / det[good]
    grad[good, 1] = (-a_xy[good] * b_x[good] + a_xx[good] * b_y[good]) / det[good]
    return grad


def glsq_hybrid_grad(mesh: MeshData, f_cell: np.ndarray, boundary_face_values: np.ndarray | None = None, alpha: float = 0.5) -> np.ndarray:
    alpha = float(np.clip(alpha, 0.0, 1.0))
    grad_gg = green_gauss_grad(mesh, f_cell, boundary_face_values)
    grad_wlsq = wlsq_grad(mesh, f_cell)
    return alpha * grad_gg + (1.0 - alpha) * grad_wlsq


def _volume_weighted_l2_error(mesh: MeshData, grad_rec: np.ndarray, grad_exact: np.ndarray) -> float:
    err_sq = np.sum((grad_rec - grad_exact) ** 2, axis=1)
    return math.sqrt(float(np.sum(err_sq * mesh.areas) / np.sum(mesh.areas)))


def _max_monotonicity_violation(mesh: MeshData, f_cell: np.ndarray, grad_rec: np.ndarray) -> float:
    f_min = f_cell.copy()
    f_max = f_cell.copy()
    if mesh.directed_i.size > 0:
        np.minimum.at(f_min, mesh.directed_i, f_cell[mesh.directed_j])
        np.maximum.at(f_max, mesh.directed_i, f_cell[mesh.directed_j])

    cmax = 0.0
    if mesh.internal_i.size > 0:
        i = mesh.internal_i
        j = mesh.internal_j

        ri = mesh.internal_fc - mesh.centers[i]
        rj = mesh.internal_fc - mesh.centers[j]

        rec_i = f_cell[i] + np.einsum("ij,ij->i", grad_rec[i], ri)
        rec_j = f_cell[j] + np.einsum("ij,ij->i", grad_rec[j], rj)

        denom_i = np.maximum(f_max[i] - f_min[i], EPS)
        denom_j = np.maximum(f_max[j] - f_min[j], EPS)

        ov_i = np.maximum.reduce([rec_i - f_max[i], f_min[i] - rec_i, np.zeros_like(rec_i)])
        ov_j = np.maximum.reduce([rec_j - f_max[j], f_min[j] - rec_j, np.zeros_like(rec_j)])
        cmax = max(cmax, float(np.max(ov_i / denom_i)), float(np.max(ov_j / denom_j)))

    if mesh.boundary_i.size > 0:
        bi = mesh.boundary_i
        rb = mesh.boundary_fc - mesh.centers[bi]
        rec_b = f_cell[bi] + np.einsum("ij,ij->i", grad_rec[bi], rb)
        denom_b = np.maximum(f_max[bi] - f_min[bi], EPS)
        ov_b = np.maximum.reduce([rec_b - f_max[bi], f_min[bi] - rec_b, np.zeros_like(rec_b)])
        cmax = max(cmax, float(np.max(ov_b / denom_b)))
    return cmax


def _regime_fractions(z_vals: np.ndarray) -> tuple[float, float, float]:
    high = float(np.mean(z_vals > 6.0) * 100.0)
    trans = float(np.mean((z_vals >= 3.0) & (z_vals <= 6.0)) * 100.0)
    low = float(np.mean(z_vals < 3.0) * 100.0)
    return high, trans, low


def _reconstruct_by_scheme(
    mesh: MeshData,
    scheme: str,
    f_cell: np.ndarray,
    boundary_face_values: np.ndarray,
    alpha: float,
) -> np.ndarray:
    if scheme == "gg":
        return green_gauss_grad(mesh, f_cell, boundary_face_values)
    if scheme == "wlsq":
        return wlsq_grad(mesh, f_cell)
    if scheme == "glsq":
        return glsq_hybrid_grad(mesh, f_cell, boundary_face_values, alpha=alpha)
    raise ValueError(f"Unsupported scheme: {scheme}")


def manufactured_solution_test(mesh_folder: str | Path, scheme: str, alpha: float = 0.5) -> dict[str, Any]:
    mesh = load_mesh(mesh_folder)
    f_cell = _manufactured_field(mesh.centers)
    grad_exact = _manufactured_grad(mesh.centers)
    boundary_face_values = _manufactured_field(mesh.boundary_fc) if mesh.boundary_i.size > 0 else np.empty(0, dtype=float)

    t0 = time.perf_counter()
    grad_rec = _reconstruct_by_scheme(mesh, scheme, f_cell, boundary_face_values, alpha)
    elapsed_s = time.perf_counter() - t0

    l2_error = _volume_weighted_l2_error(mesh, grad_rec, grad_exact)
    cmax = _max_monotonicity_violation(mesh, f_cell, grad_rec)
    high_pct, trans_pct, low_pct = _regime_fractions(mesh.z)
    throughput = float(mesh.centers.shape[0] / max(elapsed_s, EPS))

    return {
        "mesh_name": mesh.name,
        "mesh_folder": str(mesh.folder),
        "theta_target": mesh.target_theta,
        "scheme": scheme,
        "alpha": float(alpha) if scheme == "glsq" else np.nan,
        "l2_error": float(l2_error),
        "cmax": float(cmax),
        "time_ms": float(elapsed_s * 1000.0),
        "throughput_cells_per_s": throughput,
        "n_cells": int(mesh.centers.shape[0]),
        "z_mean": float(np.mean(mesh.z)),
        "z_min": float(np.min(mesh.z)),
        "z_max": float(np.max(mesh.z)),
        "regime_high_pct": high_pct,
        "regime_trans_pct": trans_pct,
        "regime_low_pct": low_pct,
    }


def _discover_mesh_dirs(mesh_dir: Path) -> list[Path]:
    if not mesh_dir.exists():
        raise FileNotFoundError(f"Mesh directory does not exist: {mesh_dir}")
    dirs: list[Path] = []
    for d in mesh_dir.iterdir():
        if not d.is_dir():
            continue
        has_vtk = (d / "mesh.vtk").exists()
        has_npy = (d / "points.npy").exists() and (d / "tri.npy").exists()
        if has_vtk or has_npy:
            dirs.append(d.resolve())
    dirs.sort(key=lambda p: (_parse_target_theta(p.name) is None, _parse_target_theta(p.name) or 0.0, p.name))
    return dirs


def _make_run_directory(base_dir: Path) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{date.today().isoformat()}_run"
    run_dir = base_dir / stem
    idx = 1
    while run_dir.exists():
        run_dir = base_dir / f"{stem}_{idx:02d}"
        idx += 1
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "raw").mkdir(parents=True, exist_ok=True)
    (run_dir / "plots").mkdir(parents=True, exist_ok=True)
    return run_dir


def _safe_get_error(rows: list[dict[str, Any]], scheme: str, alpha: float | None = None) -> float | None:
    for row in rows:
        if row["scheme"] != scheme:
            continue
        if scheme == "glsq":
            if alpha is None:
                continue
            if abs(float(row["alpha"]) - alpha) > 1.0e-12:
                continue
        return float(row["l2_error"])
    return None


def _safe_get_time(rows: list[dict[str, Any]], scheme: str, alpha: float | None = None) -> float | None:
    for row in rows:
        if row["scheme"] != scheme:
            continue
        if scheme == "glsq":
            if alpha is None:
                continue
            if abs(float(row["alpha"]) - alpha) > 1.0e-12:
                continue
        return float(row["time_ms"])
    return None


def _format_table_value(value: float | None, sci: bool = False, unit: str = "") -> str:
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return "N/A"
    if sci:
        return f"{value:.3e}{unit}"
    return f"{value:.3f}{unit}"


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _build_summary_rows(controlled_dirs: list[Path], metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_mesh: dict[str, list[dict[str, Any]]] = {}
    for m in metrics:
        if m.get("mesh_type") != "controlled":
            continue
        by_mesh.setdefault(m["mesh_name"], []).append(m)

    summary: list[dict[str, Any]] = []
    for mesh_dir in controlled_dirs:
        name = mesh_dir.name
        mesh_rows = by_mesh.get(name, [])
        if not mesh_rows:
            continue

        theta_target = _parse_target_theta(name)
        z_min = float(mesh_rows[0]["z_min"])
        z_max = float(mesh_rows[0]["z_max"])
        z_mean = float(mesh_rows[0]["z_mean"])
        gg_error = _safe_get_error(mesh_rows, "gg")
        wlsq_error = _safe_get_error(mesh_rows, "wlsq")
        glsq_05_error = _safe_get_error(mesh_rows, "glsq", 0.5)
        hybrid_adv = None
        if gg_error is not None and wlsq_error is not None and glsq_05_error is not None and glsq_05_error > 0.0:
            hybrid_adv = max(gg_error, wlsq_error) / glsq_05_error

        gg_time = _safe_get_time(mesh_rows, "gg")
        wlsq_time = _safe_get_time(mesh_rows, "wlsq")
        glsq_time = _safe_get_time(mesh_rows, "glsq", 0.5)
        summary.append(
            {
                "mesh_name": name,
                "theta_target": theta_target if theta_target is not None else np.nan,
                "theta_label": f"{int(theta_target):d}°" if theta_target is not None else name,
                "z_range_mean": f"{z_min:.2f}-{z_max:.2f} ({z_mean:.2f})",
                "z_min": z_min,
                "z_max": z_max,
                "z_mean": z_mean,
                "pure_lsq_error": wlsq_error if wlsq_error is not None else np.nan,
                "pure_gg_error": gg_error if gg_error is not None else np.nan,
                "glsq_05_error": glsq_05_error if glsq_05_error is not None else np.nan,
                "hybrid_advantage": hybrid_adv if hybrid_adv is not None else np.nan,
                "gg_time_ms": gg_time if gg_time is not None else np.nan,
                "wlsq_time_ms": wlsq_time if wlsq_time is not None else np.nan,
                "glsq_05_time_ms": glsq_time if glsq_time is not None else np.nan,
                "regime_high_pct": float(mesh_rows[0]["regime_high_pct"]),
                "regime_trans_pct": float(mesh_rows[0]["regime_trans_pct"]),
                "regime_low_pct": float(mesh_rows[0]["regime_low_pct"]),
            }
        )
    summary.sort(key=lambda r: (math.isnan(float(r["theta_target"])), float(r["theta_target"]) if not math.isnan(float(r["theta_target"])) else 0.0, r["mesh_name"]))
    return summary


def _plot_error_vs_theta(summary_rows: list[dict[str, Any]], out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.array([float(r["theta_target"]) for r in summary_rows if not math.isnan(float(r["theta_target"]))], dtype=float)
    if x.size == 0:
        ax.text(0.5, 0.5, "No controlled skewness meshes found.", ha="center", va="center", transform=ax.transAxes)
    else:
        rows = [r for r in summary_rows if not math.isnan(float(r["theta_target"]))]
        x = np.array([float(r["theta_target"]) for r in rows], dtype=float)
        y_wlsq = np.array([float(r["pure_lsq_error"]) for r in rows], dtype=float)
        y_gg = np.array([float(r["pure_gg_error"]) for r in rows], dtype=float)
        y_glsq = np.array([float(r["glsq_05_error"]) for r in rows], dtype=float)

        if np.isfinite(y_wlsq).any():
            ax.plot(x, y_wlsq, marker="o", linewidth=2, label="Pure WLSQ")
        if np.isfinite(y_gg).any():
            ax.plot(x, y_gg, marker="s", linewidth=2, label="Pure GG")
        if np.isfinite(y_glsq).any():
            ax.plot(x, y_glsq, marker="^", linewidth=2, label="GLSQ (α=0.5)")
        ax.set_yscale("log")
        ax.set_xlabel("Target θ_skew (deg)")
        ax.set_ylabel("Volume-weighted L2 gradient error")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
    ax.set_title("Gradient Error vs Target θ_skew")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def _plot_hybrid_adv_vs_z(summary_rows: list[dict[str, Any]], out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    rows = [r for r in summary_rows if math.isfinite(float(r["hybrid_advantage"]))]
    if not rows:
        ax.text(0.5, 0.5, "GLSQ (α=0.5) data unavailable.\nHybrid advantage plot not applicable.", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    else:
        rows = sorted(rows, key=lambda r: float(r["z_mean"]))
        x = np.array([float(r["z_mean"]) for r in rows], dtype=float)
        y = np.array([float(r["hybrid_advantage"]) for r in rows], dtype=float)
        ax.plot(x, y, marker="o", linewidth=2)
        ax.scatter(x, y, s=40)
        ax.set_xlabel("Mean z")
        ax.set_ylabel("Hybrid advantage = max(pure)/GLSQ(α=0.5)")
        ax.grid(True, alpha=0.3)
        ax.set_title("Hybrid Advantage Ratio vs z")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def _choose_representative_mesh(summary_rows: list[dict[str, Any]]) -> str | None:
    rows = [r for r in summary_rows if math.isfinite(float(r["hybrid_advantage"]))]
    if rows:
        rows.sort(key=lambda r: abs(float(r["z_mean"]) - 4.5))
        return rows[0]["mesh_name"]
    if summary_rows:
        return summary_rows[len(summary_rows) // 2]["mesh_name"]
    return None


def _plot_representative_mesh(
    mesh_name: str | None,
    controlled_dirs: list[Path],
    summary_rows: list[dict[str, Any]],
    selected_schemes: set[str],
    out_path: Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    if mesh_name is None:
        for ax in axes:
            ax.text(0.5, 0.5, "No mesh data available.", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
        fig.tight_layout()
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return

    mesh_dir_lookup = {d.name: d for d in controlled_dirs}
    mesh_dir = mesh_dir_lookup[mesh_name]
    mesh = load_mesh(mesh_dir)
    f_cell = _manufactured_field(mesh.centers)
    grad_exact = _manufactured_grad(mesh.centers)
    bvals = _manufactured_field(mesh.boundary_fc) if mesh.boundary_i.size > 0 else np.empty(0, dtype=float)

    scheme = "glsq" if "glsq" in selected_schemes else ("wlsq" if "wlsq" in selected_schemes else "gg")
    alpha = 0.5 if scheme == "glsq" else 0.0
    grad_rec = _reconstruct_by_scheme(mesh, scheme, f_cell, bvals, alpha=alpha)
    err_mag = np.linalg.norm(grad_rec - grad_exact, axis=1)

    tpc1 = axes[0].tripcolor(mesh.points[:, 0], mesh.points[:, 1], mesh.tri, mesh.z, shading="flat", cmap="viridis")
    axes[0].set_title(f"{mesh.name}: z-field")
    axes[0].set_aspect("equal")
    fig.colorbar(tpc1, ax=axes[0], fraction=0.046, pad=0.04)

    tpc2 = axes[1].tripcolor(mesh.points[:, 0], mesh.points[:, 1], mesh.tri, err_mag, shading="flat", cmap="inferno")
    if scheme == "glsq":
        axes[1].set_title(f"{mesh.name}: |grad error| (GLSQ α=0.5)")
    else:
        axes[1].set_title(f"{mesh.name}: |grad error| ({scheme.upper()})")
    axes[1].set_aspect("equal")
    fig.colorbar(tpc2, ax=axes[1], fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def _plot_regime_histogram(summary_rows: list[dict[str, Any]], out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    if not summary_rows:
        ax.text(0.5, 0.5, "No data for regime histogram.", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    else:
        labels = [r["theta_label"] for r in summary_rows]
        high = np.array([float(r["regime_high_pct"]) for r in summary_rows], dtype=float)
        trans = np.array([float(r["regime_trans_pct"]) for r in summary_rows], dtype=float)
        low = np.array([float(r["regime_low_pct"]) for r in summary_rows], dtype=float)
        x = np.arange(len(labels))
        ax.bar(x, high, label="High-z (>6)")
        ax.bar(x, trans, bottom=high, label="Transition (3-6)")
        ax.bar(x, low, bottom=high + trans, label="Low-z (<3)")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 100)
        ax.set_ylabel("Cell fraction (%)")
        ax.set_title("Regime Histogram Summary")
        ax.legend()
        ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def _assess_hypothesis(summary_rows: list[dict[str, Any]]) -> tuple[str, str]:
    rows = [r for r in summary_rows if math.isfinite(float(r["hybrid_advantage"]))]
    if not rows:
        return (
            "falsified",
            "Phase-transition hypothesis falsified because GLSQ (α=0.5) hybrid-advantage data is unavailable in this run.",
        )
    peak = max(rows, key=lambda r: float(r["hybrid_advantage"]))
    peak_adv = float(peak["hybrid_advantage"])
    peak_z = float(peak["z_mean"])
    if 3.0 <= peak_z <= 6.0 and peak_adv >= 5.0:
        return (
            "confirmed",
            f"Phase-transition hypothesis confirmed because the peak hybrid advantage is {peak_adv:.2f}x at mean z={peak_z:.2f} (inside 3-6).",
        )
    return (
        "falsified",
        f"Phase-transition hypothesis falsified because peak hybrid advantage is {peak_adv:.2f}x at mean z={peak_z:.2f}, which does not satisfy the z∈[3,6] and advantage≥5 criterion.",
    )


def _build_mixed_preview(metrics: list[dict[str, Any]]) -> dict[str, Any] | None:
    mixed_rows = [m for m in metrics if m.get("mesh_type") == "mixed"]
    if not mixed_rows:
        return None
    name = mixed_rows[0]["mesh_name"]
    out = {
        "mesh_name": name,
        "z_range_mean": f"{mixed_rows[0]['z_min']:.2f}-{mixed_rows[0]['z_max']:.2f} ({mixed_rows[0]['z_mean']:.2f})",
        "regime_high_pct": mixed_rows[0]["regime_high_pct"],
        "regime_trans_pct": mixed_rows[0]["regime_trans_pct"],
        "regime_low_pct": mixed_rows[0]["regime_low_pct"],
        "gg_error": _safe_get_error(mixed_rows, "gg"),
        "wlsq_error": _safe_get_error(mixed_rows, "wlsq"),
        "glsq_05_error": _safe_get_error(mixed_rows, "glsq", 0.5),
    }
    return out


def _write_markdown_report(
    report_path: Path,
    run_dir: Path,
    summary_rows: list[dict[str, Any]],
    metrics: list[dict[str, Any]],
    warnings: list[str],
) -> None:
    status, hypothesis_sentence = _assess_hypothesis(summary_rows)
    mixed_preview = _build_mixed_preview(metrics)

    lines: list[str] = []
    lines.append("# Validation Report")
    lines.append("")
    lines.append(f"- Run directory: `{run_dir}`")
    lines.append(f"- Hypothesis status: **{status.upper()}**")
    lines.append("")

    lines.append("## Controlled Skewness Family")
    lines.append("")
    lines.append("| θ_skew target | z-range (mean) | Pure LSQ error | Pure GG error | GLSQ (α=0.5) error | Hybrid advantage |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for row in summary_rows:
        lsq_err = _format_table_value(float(row["pure_lsq_error"]) if math.isfinite(float(row["pure_lsq_error"])) else None, sci=True)
        gg_err = _format_table_value(float(row["pure_gg_error"]) if math.isfinite(float(row["pure_gg_error"])) else None, sci=True)
        glsq_err = _format_table_value(float(row["glsq_05_error"]) if math.isfinite(float(row["glsq_05_error"])) else None, sci=True)
        adv = _format_table_value(float(row["hybrid_advantage"]) if math.isfinite(float(row["hybrid_advantage"])) else None, sci=False, unit="x")
        lines.append(
            f"| {row['theta_label']} | {row['z_range_mean']} | {lsq_err} | {gg_err} | {glsq_err} | {adv} |"
        )
    lines.append("")

    lines.append("## Regime Statistics per Mesh")
    lines.append("")
    lines.append("| Mesh | Mean z | High-z (%) | Transition (%) | Low-z (%) |")
    lines.append("|---|---:|---:|---:|---:|")
    for row in summary_rows:
        lines.append(
            f"| {row['mesh_name']} | {row['z_mean']:.2f} | {row['regime_high_pct']:.1f} | {row['regime_trans_pct']:.1f} | {row['regime_low_pct']:.1f} |"
        )
    lines.append("")

    lines.append("## Falsification Assessment")
    lines.append("")
    lines.append(f"- {hypothesis_sentence}")
    lines.append("")

    if mixed_preview is not None:
        lines.append("## Mixed Production Mesh (Economic Test Preview)")
        lines.append("")
        lines.append("| Mesh | z-range (mean) | GG error | WLSQ error | GLSQ (α=0.5) error | High-z (%) | Transition (%) | Low-z (%) |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
        lines.append(
            "| "
            + f"{mixed_preview['mesh_name']} | {mixed_preview['z_range_mean']} | "
            + f"{_format_table_value(mixed_preview['gg_error'], sci=True)} | "
            + f"{_format_table_value(mixed_preview['wlsq_error'], sci=True)} | "
            + f"{_format_table_value(mixed_preview['glsq_05_error'], sci=True)} | "
            + f"{mixed_preview['regime_high_pct']:.1f} | {mixed_preview['regime_trans_pct']:.1f} | {mixed_preview['regime_low_pct']:.1f} |"
        )
        lines.append("")

    lines.append("## Output File Paths")
    lines.append("")
    lines.append(f"- Raw long metrics: `{run_dir / 'raw' / 'metrics_long.csv'}`")
    lines.append(f"- Summary table: `{run_dir / 'raw' / 'summary_by_mesh.csv'}`")
    lines.append(f"- Plot: `{run_dir / 'plots' / 'error_vs_theta.png'}`")
    lines.append(f"- Plot: `{run_dir / 'plots' / 'hybrid_advantage_vs_z.png'}`")
    lines.append(f"- Plot: `{run_dir / 'plots' / 'representative_mesh_z_and_error.png'}`")
    lines.append(f"- Plot: `{run_dir / 'plots' / 'regime_histogram_summary.png'}`")
    lines.append("")

    if warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def _parse_schemes(text: str) -> tuple[set[str], list[str]]:
    warnings: list[str] = []
    selected = {tok.strip().lower() for tok in text.split(",") if tok.strip()}
    unknown = selected - set(VALID_SCHEMES)
    if unknown:
        warnings.append(f"Ignoring unknown scheme(s): {', '.join(sorted(unknown))}")
        selected -= unknown
    if not selected:
        selected = set(VALID_SCHEMES)
        warnings.append("No valid scheme specified; defaulting to gg,wlsq,glsq.")
    return selected, warnings


def run_full_validation() -> Path:
    parser = argparse.ArgumentParser(description="Manufactured-solution gradient validation harness.")
    script_dir = Path(__file__).resolve().parent
    parser.add_argument("--mesh-dir", type=Path, default=script_dir / "meshes_v3", help="Directory with controlled mesh subfolders.")
    parser.add_argument("--output-dir", type=Path, default=script_dir / "results", help="Base output directory for dated run folders.")
    parser.add_argument("--schemes", type=str, default="gg,wlsq,glsq", help="Comma-separated schemes: gg,wlsq,glsq")
    parser.add_argument("--mixed-path", type=Path, default=None, help="Optional mixed production mesh folder.")
    args = parser.parse_args()

    np.random.seed(42)

    selected_schemes, warnings = _parse_schemes(args.schemes)
    controlled_dirs = _discover_mesh_dirs(args.mesh_dir.resolve())
    mixed_dir = args.mixed_path.resolve() if args.mixed_path is not None else None

    include_mixed = False
    if mixed_dir is not None:
        if (mixed_dir / "mesh.vtk").exists() or ((mixed_dir / "points.npy").exists() and (mixed_dir / "tri.npy").exists()):
            include_mixed = True
        else:
            warnings.append(f"Mixed path ignored (no mesh found): {mixed_dir}")

    print(f"Found {len(controlled_dirs)} controlled skewness meshes + {1 if include_mixed else 0} mixed.")
    run_dir = _make_run_directory(args.output_dir.resolve())
    print(f"Writing outputs to: {run_dir}")

    metrics: list[dict[str, Any]] = []
    for mesh_dir in controlled_dirs:
        if "gg" in selected_schemes:
            row = manufactured_solution_test(mesh_dir, scheme="gg")
            row["mesh_type"] = "controlled"
            metrics.append(row)
        if "wlsq" in selected_schemes:
            row = manufactured_solution_test(mesh_dir, scheme="wlsq")
            row["mesh_type"] = "controlled"
            metrics.append(row)
        if "glsq" in selected_schemes:
            for alpha in GLSQ_ALPHAS:
                row = manufactured_solution_test(mesh_dir, scheme="glsq", alpha=alpha)
                row["mesh_type"] = "controlled"
                metrics.append(row)

    if include_mixed and mixed_dir is not None:
        if "gg" in selected_schemes:
            row = manufactured_solution_test(mixed_dir, scheme="gg")
            row["mesh_type"] = "mixed"
            metrics.append(row)
        if "wlsq" in selected_schemes:
            row = manufactured_solution_test(mixed_dir, scheme="wlsq")
            row["mesh_type"] = "mixed"
            metrics.append(row)
        if "glsq" in selected_schemes:
            for alpha in GLSQ_ALPHAS:
                row = manufactured_solution_test(mixed_dir, scheme="glsq", alpha=alpha)
                row["mesh_type"] = "mixed"
                metrics.append(row)

    metrics_path = run_dir / "raw" / "metrics_long.csv"
    metric_fields = [
        "mesh_type",
        "mesh_name",
        "mesh_folder",
        "theta_target",
        "scheme",
        "alpha",
        "l2_error",
        "cmax",
        "time_ms",
        "throughput_cells_per_s",
        "n_cells",
        "z_mean",
        "z_min",
        "z_max",
        "regime_high_pct",
        "regime_trans_pct",
        "regime_low_pct",
    ]
    _write_csv(metrics_path, metrics, metric_fields)

    summary_rows = _build_summary_rows(controlled_dirs, metrics)
    summary_path = run_dir / "raw" / "summary_by_mesh.csv"
    summary_fields = [
        "mesh_name",
        "theta_target",
        "theta_label",
        "z_range_mean",
        "z_min",
        "z_max",
        "z_mean",
        "pure_lsq_error",
        "pure_gg_error",
        "glsq_05_error",
        "hybrid_advantage",
        "gg_time_ms",
        "wlsq_time_ms",
        "glsq_05_time_ms",
        "regime_high_pct",
        "regime_trans_pct",
        "regime_low_pct",
    ]
    _write_csv(summary_path, summary_rows, summary_fields)

    plots_dir = run_dir / "plots"
    _plot_error_vs_theta(summary_rows, plots_dir / "error_vs_theta.png")
    _plot_hybrid_adv_vs_z(summary_rows, plots_dir / "hybrid_advantage_vs_z.png")
    rep_name = _choose_representative_mesh(summary_rows)
    _plot_representative_mesh(rep_name, controlled_dirs, summary_rows, selected_schemes, plots_dir / "representative_mesh_z_and_error.png")
    _plot_regime_histogram(summary_rows, plots_dir / "regime_histogram_summary.png")

    report_path = run_dir / "validation_report.md"
    _write_markdown_report(report_path, run_dir, summary_rows, metrics, warnings)
    print(f"Validation report: {report_path}")
    return run_dir


if __name__ == "__main__":
    run_full_validation()
