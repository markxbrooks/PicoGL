"""GLMesh.draw must use uploaded GPU counts after MeshData.delete()."""

from unittest.mock import MagicMock, patch

import numpy as np

from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.draw_spec import MeshDrawInfo
from picogl.renderer.glmesh import GLMesh
from picogl.renderer.meshdata import MeshData


def test_draw_after_cpu_mesh_delete_uses_uploaded_index_count() -> None:
    """Sheet-style path: copy into GLMesh, drop CPU arrays, then upload/draw."""
    vertices = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]],
        dtype=np.float32,
    )
    faces = np.array([0, 1, 2, 1, 3, 2], dtype=np.uint32)
    colors = np.ones((4, 3), dtype=np.float32)
    normals = np.tile([0.0, 0.0, 1.0], (4, 1)).astype(np.float32)

    mesh_data = MeshData(
        vertices=vertices,
        indices=faces,
        colors=colors,
        normals=normals,
    )
    glmesh = GLMesh.from_mesh_data(mesh_data)
    mesh_data.delete()

    mock_vao = MagicMock()
    with patch("picogl.renderer.glmesh.VertexArrayObject", return_value=mock_vao):
        glmesh.upload()
    glmesh.draw()

    mock_vao.draw.assert_called_once()
    kwargs = mock_vao.draw.call_args.kwargs
    assert kwargs.get("index_count") == len(faces)
    assert kwargs.get("mode") == GLDrawMode.TRIANGLES


def test_draw_mode_override_with_cpu_mesh_intact() -> None:
    """Gizmo path: attached CPU MeshData still honors GLMesh.draw(mode=LINES)."""
    vertices = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
        dtype=np.float32,
    )
    colors = np.ones((2, 3), dtype=np.float32)
    mesh_data = MeshData(
        vertices=vertices,
        colors=colors,
        draw_info=MeshDrawInfo(mode=GLDrawMode.TRIANGLES, indexed=False),
    )
    glmesh = GLMesh.from_mesh_data(mesh_data)
    mock_vao = MagicMock()
    with patch("picogl.renderer.glmesh.VertexArrayObject", return_value=mock_vao):
        glmesh.upload()
    glmesh.draw(mode=GLDrawMode.LINES)

    mock_vao.draw.assert_called_once()
    kwargs = mock_vao.draw.call_args.kwargs
    assert kwargs.get("mode") == GLDrawMode.LINES
    assert kwargs.get("index_count") == 2
