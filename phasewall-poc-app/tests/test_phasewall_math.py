from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from phasewall_poc.geometry import compute_curvature_sign, mahalanobis_radius
from phasewall_poc.phasewall import apply_phase_wall_z


def test_apply_phase_wall_direction_and_clamp() -> None:
    z = np.array([[0.0, 0.0, 5.0], [0.2, 0.1, 0.0]])
    out_high = apply_phase_wall_z(z, r0=1.0, strength=2.0)
    out_one = apply_phase_wall_z(z, r0=1.0, strength=1.0)
    assert_allclose(out_high, out_one)

    # Direction preserved for the outlier vector.
    cos = np.dot(z[0], out_one[0]) / (np.linalg.norm(z[0]) * np.linalg.norm(out_one[0]))
    assert abs(cos - 1.0) < 1e-12


def test_curvature_sign_flip_at_sigma() -> None:
    r = np.array([0.9, 1.0, 1.1])
    sign = compute_curvature_sign(r, sigma=1.0)
    assert np.array_equal(sign, np.array([1, 0, -1]))


def test_mahalanobis_identity_matches_euclidean() -> None:
    pts = np.array([[3.0, 4.0], [1.0, 1.0]])
    mean = np.zeros(2)
    cov = np.eye(2)
    m = mahalanobis_radius(pts, mean, cov)
    e = np.linalg.norm(pts, axis=1)
    assert_allclose(m, e)
