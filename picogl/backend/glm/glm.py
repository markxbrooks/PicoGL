"""
A module for handling matrix and vector operations using the `pyglm` and `numpy` libraries.

This module provides utility functions for creating, converting, and manipulating
matrices (`mat4`) and vectors (`vec4`) compatible with the `pyglm` library, as well as
converting between `pyglm` and `numpy` data structures.

The module also includes functions for calculating perspective projection matrices
commonly used in graphics programming.
"""

from __future__ import annotations

import numpy as np
from pyglm import glm
from pyglm.glm import vec4

Mat4 = glm.mat4


def glm_identity_matrix() -> Mat4:
    return glm.mat4(1.0)


def as_glm_mat4(m) -> glm.mat4:
    if isinstance(m, glm.mat4):
        return m
    if isinstance(m, np.ndarray):
        arr = np.asarray(m, dtype=np.float32).reshape(4, 4)
        # glm.mat4(c0,c1,c2,c3) takes *columns*. Must use arr[:,j], not arr[j,:];
        # rows were wrongly used here before, which transposed asymmetric matrices
        # (e.g. MVP) and caused extreme perspective / “ray” artifacts after Phase 3.
        return glm.mat4(
            glm_vec4(arr[0, 0], arr[1, 0], arr[2, 0], arr[3, 0]),
            glm_vec4(arr[0, 1], arr[1, 1], arr[2, 1], arr[3, 1]),
            glm_vec4(arr[0, 2], arr[1, 2], arr[2, 2], arr[3, 2]),
            glm_vec4(arr[0, 3], arr[1, 3], arr[2, 3], arr[3, 3]),
        )
    return glm.mat4(m)


def glm_vec4(arg1, arg2, arg3, arg4) -> vec4:
    """glm_vec4 """
    return glm.vec4(arg1, arg2, arg3, arg4)


def glm_mat4_to_np(m) -> np.ndarray:
    """Row-major 4x4 like legacy NumPy camera matrices (not raw ``value_ptr`` layout)."""
    if m is None:
        raise ValueError("matrix is None")
    if isinstance(m, np.ndarray):
        return np.asarray(m, dtype=np.float32).reshape(4, 4)
    if isinstance(m, glm.mat4):
        # pyglm: m[c] is column c; element at row r is m[c][r]. Legacy uses out[r,c]=M[r,c].
        return np.array(
            [[m[c][r] for c in range(4)] for r in range(4)],
            dtype=np.float32,
        )
    return np.frombuffer(glm.value_ptr(m), dtype=np.float32).reshape(4, 4)


def glm_compute_projection_matrix(
    aspect: float,
    *,
    fov_deg: float = 45.0,
    near: float = 0.1,
    far: float = 500.0,
) -> glm.mat4:
    """glm_compute_projection_matrix """
    return glm.perspective(glm.radians(fov_deg), float(aspect), near, far)