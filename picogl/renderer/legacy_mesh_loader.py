"""Load an OBJ into a ``LegacyGLMesh`` (CPU-side; upload after a GL context exists)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from picogl.renderer import MeshData
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.utils.loader.object import ObjectLoader


def load_legacy_mesh(
    path: Path | str,
    color: tuple[float, float, float] = (1.0, 0.0, 0.0),
    *,
    upload: bool = False,
) -> LegacyGLMesh:
    """Load an OBJ file as a legacy mesh.

    Parameters
    ----------
    path:
        Path to an ``.obj`` file.
    color:
        Solid RGB color applied to every vertex.
    upload:
        If True, call ``mesh.upload()`` immediately (requires a current GL context).
        Prefer False and upload after GLUT/Qt creates a context.
    """
    obj_loader = ObjectLoader(str(path))
    object_data = obj_loader.to_array_style()

    vertices = np.asarray(object_data.vertices, dtype=np.float32).reshape(-1, 3)
    vertex_count = int(vertices.shape[0])

    if (
        getattr(object_data, "indices", None) is not None
        and len(object_data.indices) > 0
    ):
        faces = np.asarray(object_data.indices, dtype=np.uint32).reshape(-1, 3)
    else:
        if vertex_count % 3 != 0:
            raise ValueError(
                f"Triangle-soup vertex count {vertex_count} is not divisible by 3"
            )
        faces = np.arange(vertex_count, dtype=np.uint32).reshape(-1, 3)

    normals = None
    if (
        getattr(object_data, "normals", None) is not None
        and len(object_data.normals) > 0
    ):
        normals = np.asarray(object_data.normals, dtype=np.float32).reshape(-1, 3)

    mesh_data = MeshData.from_raw(
        vertices=vertices,
        normals=normals,
        indices=faces.reshape(-1),
        color_per_vertex=list(color),
    )

    mesh = LegacyGLMesh(
        vertices=mesh_data.vertices,
        faces=faces,
        colors=mesh_data.colors,
        normals=mesh_data.normals,
    )
    if upload:
        mesh.upload()
    return mesh
