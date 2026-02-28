from __future__ import annotations

import numpy as np

from .geometry import mahalanobis_radius


def apply_phase_wall_z(z: np.ndarray, r0: float, strength: float = 0.4) -> np.ndarray:
    strength = float(np.clip(strength, 0.0, 1.0))
    z_out = np.asarray(z, dtype=float).copy()

    single = z_out.ndim == 1
    if single:
        z_out = z_out[np.newaxis, :]

    norms = np.linalg.norm(z_out, axis=1)
    outside = norms > r0
    if np.any(outside):
        scale = 1.0 - strength * (1.0 - r0 / norms[outside])
        scale = np.clip(scale, 0.0, 1.0)
        z_out[outside] *= scale[:, None]

    if single:
        return z_out[0]
    return z_out


def hard_project_to_radius(z: np.ndarray, r0: float) -> np.ndarray:
    z_out = np.asarray(z, dtype=float).copy()
    single = z_out.ndim == 1
    if single:
        z_out = z_out[np.newaxis, :]
    norms = np.linalg.norm(z_out, axis=1)
    outside = norms > r0
    if np.any(outside):
        z_out[outside] *= (r0 / norms[outside])[:, None]
    return z_out[0] if single else z_out


def decompose_radial_tangential(vectors: np.ndarray, positions: np.ndarray, eps: float = 1e-12) -> tuple[np.ndarray, np.ndarray]:
    v = np.asarray(vectors, dtype=float)
    p = np.asarray(positions, dtype=float)
    norms = np.linalg.norm(p, axis=1, keepdims=True)
    safe = np.where(norms > eps, norms, 1.0)
    radial_hat = p / safe

    radial_mag = np.sum(v * radial_hat, axis=1, keepdims=True)
    radial = radial_mag * radial_hat
    tangential = v - radial
    return radial, tangential


def phase_aware_noise(
    positions: np.ndarray,
    noise: np.ndarray,
    r0: float = 1.0,
    strength: float = 0.4,
    tangential_damping: float = 0.8,
    radial_boost: float = 0.25,
) -> np.ndarray:
    p = np.asarray(positions, dtype=float)
    n = np.asarray(noise, dtype=float).copy()
    r = np.linalg.norm(p, axis=1)
    outside = r > r0
    if not np.any(outside):
        return n

    strength = float(np.clip(strength, 0.0, 1.0))
    radial, tangential = decompose_radial_tangential(n[outside], p[outside])

    inward = -radial
    adjusted = (
        radial
        + strength * radial_boost * inward
        + (1.0 - strength * tangential_damping) * tangential
    )
    n[outside] = adjusted
    return n


def mahalanobis_phase_wall(
    points: np.ndarray,
    mean: np.ndarray,
    cov: np.ndarray,
    r0: float = 1.0,
    strength: float = 0.4,
) -> np.ndarray:
    pts = np.asarray(points, dtype=float)
    mu = np.asarray(mean, dtype=float)
    cov_arr = np.asarray(cov, dtype=float)

    radii = mahalanobis_radius(pts, mu, cov_arr)
    outside = radii > r0
    if not np.any(outside):
        return pts.copy()

    evals, evecs = np.linalg.eigh(cov_arr)
    evals = np.clip(evals, 1e-12, None)

    centered = pts - mu
    whitened = centered @ evecs @ np.diag(1.0 / np.sqrt(evals))
    whitened_damped = apply_phase_wall_z(whitened, r0=r0, strength=strength)
    restored = whitened_damped @ np.diag(np.sqrt(evals)) @ evecs.T + mu
    return restored
