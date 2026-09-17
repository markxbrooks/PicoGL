"""
A collection of utility functions for processing and normalizing data into
array-like structures or specific container types.

This module provides functions to convert input data, such as lists or arrays,
into standardized formats that are used in 3D rendering contexts, such as `MeshData`.
"""

from typing import Any

import numpy as np
from numpy import dtype, generic


def as_vec3_array(data: Any) -> np.ndarray:
    """Convert data to a float32 ``(N, 3)`` NumPy array.

    Raises
    ------
    ValueError
        If the resulting array does not have shape ``(N, 3)``.
        positions = np.asarray(data, dtype=np.float32).reshape(-1, 3) is the faster way of doing this
        [1, 2, 3, 4, 5, 6]
        becomes
        [[1, 2, 3],
        [4, 5, 6]]
    """
    array = np.asarray(data, dtype=np.float32)

    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError(
            f"expected data with shape (N, 3), got {array.shape}"
        )

    return array


def as_meshdata(
    colors: Any, normals: Any, positions: Any, indices: Any = None
) -> "MeshData":
    """Normalize raw strand arrays/lists into a MeshData container."""
    from picogl.backend.gl.enums import GLDrawMode
    from picogl.renderer import MeshData
    from picogl.renderer.draw_spec import MeshDrawInfo

    v = as_vec3_array(positions)
    n = as_vec3_array(normals)
    c = as_vec3_array(colors)
    if indices is None:
        return MeshData(
            vertices=v,
            normals=n,
            colors=c,
            draw_info=MeshDrawInfo(mode=GLDrawMode.TRIANGLES, indexed=False),
        )
    i = np.asarray(indices, dtype=np.int32)
    return MeshData(
        vertices=v,
        normals=n,
        colors=c,
        indices=i,
        draw_info=MeshDrawInfo(mode=GLDrawMode.TRIANGLES, indexed=True),
    )
