"""Tests for MeshDrawInfo / MeshDrawSpec topology mapping."""

from __future__ import annotations

import numpy as np
from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.draw_spec import MeshDrawInfo, compute_draw_spec
from picogl.renderer.meshdata import MeshData
from picogl.renderer.molecular import AtomsMesh, BondsMesh


def test_compute_draw_spec_cylinder_full_and_slice() -> None:
    info = MeshDrawInfo(
        mode=GLDrawMode.TRIANGLES,
        indexed=True,
        elements_per_item=96,
        vertices_per_item=16,
    )
    full = compute_draw_spec(info, index_count=10 * 96, vertex_count=10 * 16)
    assert full.mode == GLDrawMode.TRIANGLES
    assert full.indexed is True
    assert full.count == 960
    assert full.pointer == 0

    mid = compute_draw_spec(
        info,
        index_count=40 * 96,
        vertex_count=40 * 16,
        first_item=20,
        item_count=10,
    )
    assert mid.count == 960
    assert mid.pointer == 20 * 96 * 4

    past_end = compute_draw_spec(
        info,
        index_count=10 * 96,
        vertex_count=10 * 16,
        first_item=20,
        item_count=10,
    )
    assert past_end.count == 0


def test_compute_draw_spec_clamps_to_index_buffer() -> None:
    info = MeshDrawInfo(
        mode=GLDrawMode.TRIANGLES, indexed=True, elements_per_item=6
    )
    spec = compute_draw_spec(info, index_count=10, first_item=1, item_count=3)
    # 1*6=6 start, 3*6=18 requested, clamp to 10-6=4
    assert spec.count == 4
    assert spec.pointer == 6 * 4


def test_compute_draw_spec_line_bonds() -> None:
    info = MeshDrawInfo(mode=GLDrawMode.LINES, indexed=True)
    spec = compute_draw_spec(info, index_count=20, item_count=None)
    assert spec.mode == GLDrawMode.LINES
    assert spec.count == 20
    assert spec.indexed is True


def test_compute_draw_spec_points() -> None:
    info = MeshDrawInfo(mode=GLDrawMode.POINTS, indexed=False)
    spec = compute_draw_spec(
        info, vertex_count=100, first_item=10, item_count=5
    )
    assert spec.mode == GLDrawMode.POINTS
    assert spec.count == 5
    assert spec.first == 10
    assert spec.indexed is False


def test_meshdata_draw_spec_and_expand_colors() -> None:
    mesh = MeshData(
        vertices=np.zeros((6, 3), dtype=np.float32),
        colors=np.zeros((6, 3), dtype=np.float32),
        indices=np.arange(12, dtype=np.uint32),
        draw_info=MeshDrawInfo(
            mode=GLDrawMode.TRIANGLES,
            indexed=True,
            elements_per_item=6,
            vertices_per_item=3,
        ),
    )
    spec = mesh.draw_spec(first_item=1, item_count=1)
    assert spec.count == 6
    assert spec.pointer == 6 * 4

    logical = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)
    expanded = mesh.expand_attribute_per_item(logical, 3)
    assert expanded.shape == (6, 3)
    np.testing.assert_allclose(expanded[0], (1.0, 0.0, 0.0))
    np.testing.assert_allclose(expanded[3], (0.0, 1.0, 0.0))

    mesh.color_source_indices = np.array([0, 0, 0, 1, 1, 1], dtype=np.uint32)
    gathered = mesh.expand_colors(logical)
    np.testing.assert_allclose(gathered[2], (1.0, 0.0, 0.0))
    np.testing.assert_allclose(gathered[5], (0.0, 1.0, 0.0))


def test_atoms_mesh_stamps_draw_info() -> None:
    class _Atom:
        def __init__(self) -> None:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
            self.chain_id = "A"

    data = AtomsMesh([_Atom()], slices=4, stacks=4).to_mesh_data()
    assert data.draw_info is not None
    assert data.draw_info.mode == GLDrawMode.TRIANGLES
    assert data.draw_info.indexed is True
    spec = data.draw_spec(item_count=1)
    assert spec.count == data.draw_info.elements_per_item
    assert spec.count == int(np.asarray(data.indices).size)


def test_bonds_mesh_stamps_draw_info() -> None:
    class _Atom:
        def __init__(self, x: float) -> None:
            self.x = x
            self.y = 0.0
            self.z = 0.0
            self.chain_id = "A"

    data = BondsMesh(
        [(_Atom(0.0), _Atom(1.0))], segments=8
    ).to_mesh_data()
    assert data.draw_info is not None
    assert data.draw_info.elements_per_item == 48
    assert data.draw_info.vertices_per_item == 16
    spec = data.draw_spec(item_count=1)
    assert spec.count == 48
    assert spec.mode == GLDrawMode.TRIANGLES
