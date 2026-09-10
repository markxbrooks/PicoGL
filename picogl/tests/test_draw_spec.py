"""Tests for MeshDrawInfo / MeshDrawSpec and MeshData.draw_spec."""

from __future__ import annotations

import numpy as np
from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.draw_spec import MeshDrawInfo, MeshDrawSpec
from picogl.renderer.meshdata import MeshData


def test_meshdata_infers_draw_info_when_omitted():
    points = MeshData(
        vertices=np.zeros((3, 3), dtype=np.float32),
        colors=np.zeros((3, 3), dtype=np.float32),
    )
    assert points.draw_info.mode == GLDrawMode.POINTS
    assert points.draw_info.indexed is False

    tris = MeshData(
        vertices=np.zeros((3, 3), dtype=np.float32),
        colors=np.zeros((3, 3), dtype=np.float32),
        indices=np.array([0, 1, 2], dtype=np.uint32),
    )
    assert tris.draw_info.mode == GLDrawMode.TRIANGLES
    assert tris.draw_info.indexed is True


def test_draw_spec_points_range():
    mesh = MeshData(
        vertices=np.zeros((10, 3), dtype=np.float32),
        colors=np.zeros((10, 3), dtype=np.float32),
        draw_info=MeshDrawInfo(mode=GLDrawMode.POINTS, indexed=False),
    )
    spec = mesh.draw_spec(first_item=2, item_count=3)
    assert isinstance(spec, MeshDrawSpec)
    assert spec.mode == GLDrawMode.POINTS
    assert spec.count == 3
    assert spec.first == 2
    assert spec.pointer == 0
    assert not hasattr(spec, "indexed")


def test_draw_spec_triangle_items():
    mesh = MeshData(
        vertices=np.zeros((8, 3), dtype=np.float32),
        colors=np.zeros((8, 3), dtype=np.float32),
        indices=np.arange(24, dtype=np.uint32),
        draw_info=MeshDrawInfo(
            mode=GLDrawMode.TRIANGLES,
            indexed=True,
            elements_per_item=12,
            vertices_per_item=4,
        ),
    )
    spec = mesh.draw_spec(first_item=1, item_count=1)
    assert spec.mode == GLDrawMode.TRIANGLES
    assert spec.count == 12
    assert spec.first == 0
    assert spec.pointer == 12 * 4


def test_apply_logical_colors_repeat():
    mesh = MeshData(
        vertices=np.zeros((8, 3), dtype=np.float32),
        colors=np.zeros((8, 3), dtype=np.float32),
        draw_info=MeshDrawInfo(
            mode=GLDrawMode.TRIANGLES,
            indexed=True,
            elements_per_item=12,
            vertices_per_item=4,
        ),
    )
    logical = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    expanded = mesh.apply_logical_colors(logical)
    assert expanded.shape == (8, 3)
    np.testing.assert_allclose(mesh.colors[0], (1.0, 0.0, 0.0))
    np.testing.assert_allclose(mesh.colors[3], (1.0, 0.0, 0.0))
    np.testing.assert_allclose(mesh.colors[4], (0.0, 0.0, 1.0))
    np.testing.assert_allclose(mesh.colors[7], (0.0, 0.0, 1.0))


def test_apply_logical_colors_gather():
    mesh = MeshData(
        vertices=np.zeros((4, 3), dtype=np.float32),
        colors=np.zeros((4, 3), dtype=np.float32),
        color_source_indices=np.array([0, 0, 1, 1], dtype=np.intp),
        draw_info=MeshDrawInfo(mode=GLDrawMode.LINES, indexed=False),
    )
    logical = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)
    mesh.apply_logical_colors(logical)
    np.testing.assert_allclose(mesh.colors[0], (1.0, 0.0, 0.0))
    np.testing.assert_allclose(mesh.colors[1], (1.0, 0.0, 0.0))
    np.testing.assert_allclose(mesh.colors[2], (0.0, 1.0, 0.0))
    np.testing.assert_allclose(mesh.colors[3], (0.0, 1.0, 0.0))


def test_meshdata_draw_requires_vao():
    mesh = MeshData(
        vertices=np.zeros((3, 3), dtype=np.float32),
        colors=np.zeros((3, 3), dtype=np.float32),
    )
    try:
        mesh.draw()
    except RuntimeError as exc:
        assert "VAO" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")


def test_meshdata_draw_forwards_spec_to_vao():
    from unittest.mock import MagicMock

    mesh = MeshData(
        vertices=np.zeros((10, 3), dtype=np.float32),
        colors=np.zeros((10, 3), dtype=np.float32),
        draw_info=MeshDrawInfo(mode=GLDrawMode.POINTS, indexed=False),
    )
    vao = MagicMock()
    mesh.attach_vao(vao)
    mesh.draw(first_item=2, item_count=3)
    vao.draw.assert_called_once()
    kwargs = vao.draw.call_args.kwargs
    assert kwargs["index_count"] == 3
    assert kwargs["mode"] == GLDrawMode.POINTS
    assert kwargs["first"] == 2


def test_meshdata_draw_count_override():
    from unittest.mock import MagicMock

    mesh = MeshData(
        vertices=np.zeros((4, 3), dtype=np.float32),
        colors=np.zeros((4, 3), dtype=np.float32),
        indices=np.arange(8, dtype=np.uint32),
        draw_info=MeshDrawInfo(mode=GLDrawMode.LINES, indexed=True),
    )
    vao = MagicMock()
    mesh.attach_vao(vao)
    mesh.draw(count=2)
    assert vao.draw.call_args.kwargs["index_count"] == 2
    assert vao.draw.call_args.kwargs["mode"] == GLDrawMode.LINES


def test_glmesh_draw_delegates_to_mesh_draw():
    from unittest.mock import MagicMock

    from picogl.renderer.glmesh import GLMesh

    mesh = MeshData(
        vertices=np.zeros((3, 3), dtype=np.float32),
        colors=np.zeros((3, 3), dtype=np.float32),
        indices=np.array([0, 1, 2], dtype=np.uint32),
        draw_info=MeshDrawInfo(mode=GLDrawMode.TRIANGLES, indexed=True),
    )
    vao = MagicMock()
    mesh.attach_vao(vao)
    glmesh = GLMesh(
        vertices=mesh.vertices,
        faces=mesh.indices,
        colors=mesh.colors,
    )
    glmesh.vao = vao
    glmesh.mesh = mesh
    glmesh.draw()
    vao.draw.assert_called_once()
    assert vao.draw.call_args.kwargs["index_count"] == 3
    assert vao.draw.call_args.kwargs["mode"] == GLDrawMode.TRIANGLES
