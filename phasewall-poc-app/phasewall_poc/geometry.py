from __future__ import annotations

import numpy as np


def gaussian_hill(x: np.ndarray | float, y: np.ndarray | float, sigma: float = 1.0) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    r2 = x_arr**2 + y_arr**2
    return np.exp(-r2 / (2.0 * sigma**2))


def gaussian_gradient(points: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    pts = np.asarray(points, dtype=float)
    if pts.ndim != 2:
        raise ValueError("points must have shape (n, d)")
    if pts.shape[1] < 2:
        raise ValueError("points must have at least 2 dimensions")

    r2 = np.sum(pts[:, :2] ** 2, axis=1)
    base = np.exp(-r2 / (2.0 * sigma**2))
    grad = np.zeros_like(pts)
    grad[:, 0] = -(pts[:, 0] / sigma**2) * base
    grad[:, 1] = -(pts[:, 1] / sigma**2) * base
    return grad


def compute_curvature_sign(r: np.ndarray | float, sigma: float = 1.0, tol: float = 1e-10) -> np.ndarray:
    r_arr = np.asarray(r, dtype=float)
    val = sigma**2 - r_arr**2
    out = np.zeros_like(val, dtype=int)
    out[val > tol] = 1
    out[val < -tol] = -1
    return out


def mahalanobis_radius(points: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> np.ndarray:
    pts = np.asarray(points, dtype=float)
    mu = np.asarray(mean, dtype=float)
    cov_arr = np.asarray(cov, dtype=float)

    if pts.ndim == 1:
        pts = pts[np.newaxis, :]

    diff = pts - mu
    inv_cov = np.linalg.inv(cov_arr)
    quad = np.einsum("...i,ij,...j->...", diff, inv_cov, diff)
    quad = np.clip(quad, 0.0, None)
    return np.sqrt(quad)
