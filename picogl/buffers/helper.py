"""
A collection of utility functions for processing and normalizing data into
array-like structures or specific container types.

This module provides functions to convert input data, such as lists or arrays,
into standardized formats that are used in 3D rendering contexts, such as `MeshData`.
"""

from typing import Any

import numpy as np
from numpy import dtype, generic, ndarray


def as_vec3_array(data) -> np.ndarray[Any, dtype[generic]]:
    """as vec3 array"""
    return np.asarray(data, dtype=np.float32).reshape(-1, 3)


def as_meshdata(
    colors: Any, normals: Any, positions: Any, indices: Any = None
) -> "MeshData":
    """Normalize raw strand arrays/lists into a MeshData container."""
    from picogl.renderer import MeshData

    v = as_vec3_array(positions)
    n = as_vec3_array(normals)
    c = as_vec3_array(colors)
    if indices is None:
        return MeshData(vertices=v, normals=n, colors=c)
    i = np.asarray(indices, dtype=np.int32)
    return MeshData(vertices=v, normals=n, colors=c, indices=i)
