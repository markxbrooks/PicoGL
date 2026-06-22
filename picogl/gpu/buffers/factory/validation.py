"""
Validation of input data
"""

import numpy as np
from picogl.renderer import MeshData


def validate_mesh_data(data: MeshData):
    """validate mesh data"""
    validate_input_data(
        vertices=data.vertices,
        indices=data.indices,
        normals=data.normals,
        colors=data.colors,
    )


def validate_input_data(
    vertices: np.ndarray,
    indices: np.ndarray = None,
    normals: np.ndarray = None,
    colors: np.ndarray = None,
):
    """
    Validate mesh input data for consistency.

    Parameters
    ----------
    vertices : np.ndarray
        Required array of shape (N, 3) for vertex positions.
    indices : np.ndarray, optional
        Optional array of shape (M, 3) for triangular faces.
    normals : np.ndarray, optional
        Optional array of shape (N, 3) for vertex normals.
    colors : np.ndarray, optional
        Optional array of shape (N, 3) or (N, 4) for per-vertex colors.

    Raises
    ------
    ValueError
        If any provided array has an invalid shape or is inconsistent.
    """

    # --- Vertices (required) ---
    if (
        not isinstance(vertices, np.ndarray)
        or vertices.ndim != 2
        or vertices.shape[1] != 3
    ):
        raise ValueError(
            f"vertices must be a (N, 3) ndarray, got {vertices.shape if isinstance(vertices, np.ndarray) else type(vertices)}"
        )

    n_vertices = vertices.shape[0]

    # --- Indices (optional) ---
    if indices is not None:
        if (
            not isinstance(indices, np.ndarray)
            or indices.ndim != 2
            or indices.shape[1] != 3
        ):
            raise ValueError(
                f"indices must be a (M, 3) ndarray for triangular faces, got {indices.shape if isinstance(indices, np.ndarray) else type(indices)}"
            )
        if np.any(indices < 0) or np.any(indices >= n_vertices):
            raise ValueError("indices contain out-of-bounds vertex references")

    # --- Normals (optional) ---
    if normals is not None:
        if not isinstance(normals, np.ndarray) or normals.shape != (n_vertices, 3):
            raise ValueError(
                f"normals must be a (N, 3) ndarray matching vertices, got {normals.shape if isinstance(normals, np.ndarray) else type(normals)}"
            )

    # --- Colors (optional) ---
    if colors is not None:
        if (
            not isinstance(colors, np.ndarray)
            or colors.ndim != 2
            or colors.shape[0] != n_vertices
        ):
            raise ValueError(
                f"colors must have same number of rows as vertices, got {colors.shape if isinstance(colors, np.ndarray) else type(colors)}"
            )
        if colors.shape[1] not in (3, 4):
            raise ValueError("colors must have 3 (RGB) or 4 (RGBA) columns")

    return True
