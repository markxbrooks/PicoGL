"""Regression tests for non-indexed GLMesh geometry."""

from unittest.mock import MagicMock, patch

import numpy as np

from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.glmesh import GLMesh
from picogl.renderer.meshdata import MeshData


def _vertices() -> np.ndarray:
    return np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        dtype=np.float32,
    )


def test_glmesh_accepts_omitted_faces() -> None:
    mesh = GLMesh(vertices=_vertices())

    assert not mesh.use_indices
    assert mesh.indices.dtype == np.uint32
    assert mesh.indices.size == 0


def test_from_mesh_data_accepts_missing_indices() -> None:
    mesh_data = MeshData.from_raw(vertices=_vertices())

    mesh = GLMesh.from_mesh_data(mesh_data)

    assert not mesh.use_indices
    assert mesh.indices.size == 0


def test_non_indexed_upload_omits_ebo_and_draws_vertex_count() -> None:
    mesh = GLMesh(vertices=_vertices())
    vao = MagicMock()

    with patch("picogl.renderer.glmesh.VertexArrayObject", return_value=vao):
        mesh.upload()

    vao.add_ebo.assert_not_called()
    assert mesh.index_count == 3

    mesh.draw(mode=GLDrawMode.LINES)
    vao.draw.assert_called_once()
    assert vao.draw.call_args.kwargs["index_count"] == 3
    assert vao.draw.call_args.kwargs["mode"] == GLDrawMode.LINES
