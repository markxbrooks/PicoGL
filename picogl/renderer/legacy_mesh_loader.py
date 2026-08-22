"""Load an OBJ into an uploaded ``LegacyGLMesh``."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from picogl.renderer import MeshData
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.utils.loader.object import ObjectLoader


def load_legacy_mesh(
    path: Path | str,
    color: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> LegacyGLMesh:
    """Load an OBJ file as a GPU-ready legacy mesh.

    Vertices are treated as a triangle soup (sequential face indices) so this
    matches the teapot example's previous loading path.
    """
    obj_loader = ObjectLoader(str(path))
    object_data = obj_loader.to_array_style()
    vertex_count = len(object_data.vertices) // 3

    mesh_data = MeshData.from_raw(
        vertices=object_data.vertices,
        normals=object_data.normals,
        colors=([list(color)] * vertex_count),
    )

    mesh = LegacyGLMesh(
        vertices=mesh_data.vertices.reshape(-1, 3),
        faces=np.arange(len(mesh_data.vertices) // 3).reshape(-1, 3),
        colors=(
            mesh_data.colors.reshape(-1, 3) if mesh_data.colors is not None else None
        ),
        normals=(
            mesh_data.normals.reshape(-1, 3) if mesh_data.normals is not None else None
        ),
    )
    mesh.upload()
    return mesh
