"""ObjectRenderer draws through MeshData, not VertexArrayObject.draw directly."""

from unittest.mock import MagicMock

import numpy as np

from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.meshdata import MeshData
from picogl.renderer.object import ObjectRenderer


def test_draw_model_issues_mesh_draw_spec() -> None:
    vertices = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]],
        dtype=np.float32,
    )
    mesh = MeshData(vertices=vertices, colors=np.ones((4, 3), dtype=np.float32))
    mock_vao = MagicMock()
    mock_shader = MagicMock()
    mock_context = MagicMock()
    mock_context.vaos = {"model": mock_vao}
    mock_context.shader = mock_shader
    mock_context.mvp_matrix = np.eye(4)
    mock_context.model_matrix = np.eye(4)
    mock_context.eye_np = np.array([0.0, 0.0, 5.0])

    renderer = ObjectRenderer(context=mock_context, data=mesh, use_texture=False)
    renderer._draw_model()

    assert mesh.vao is mock_vao
    mock_vao.draw.assert_called_once()
    spec = mock_vao.draw.call_args.args[0]
    assert spec.mode == GLDrawMode.TRIANGLES
    assert spec.count == 4
    assert spec.first == 0
