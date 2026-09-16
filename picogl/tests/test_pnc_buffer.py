"""Tests for PNCBuffer mesh assembly."""

from __future__ import annotations

import numpy as np

from picogl.core.geometry.sphere import unit_sphere_mesh
from picogl.renderer.mesh_arrays import MeshArrays
from picogl.renderer.molecular.pnc_buffer import PNCBuffer


def _line_template() -> MeshArrays:
    return MeshArrays(
        positions=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
        normals=[[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        indices=[0, 1],
    )


def test_pnc_buffer_add_instance_offsets_indices() -> None:
    buf = PNCBuffer()
    template = _line_template()
    buf.add_instance((10.0, 0.0, 0.0), template, (1.0, 0.0, 0.0))
    buf.add_instance((0.0, 20.0, 0.0), template, (0.0, 1.0, 0.0))
    verts, norms, cols, idxs = buf.to_arrays()
    assert verts.shape == (4, 3)
    assert norms.shape == (4, 3)
    assert cols.shape == (4, 3)
    np.testing.assert_allclose(verts[0], (10.0, 0.0, 0.0))
    np.testing.assert_allclose(verts[2], (0.0, 20.0, 0.0))
    assert idxs.tolist() == [0, 1, 2, 3]
    np.testing.assert_allclose(cols[0], (1.0, 0.0, 0.0))
    np.testing.assert_allclose(cols[2], (0.0, 1.0, 0.0))


def test_pnc_buffer_add_instance_uses_template_length() -> None:
    buf = PNCBuffer()
    template = MeshArrays(
        positions=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        normals=[[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        indices=[0, 1, 2],
    )
    buf.add_instance((0.0, 0.0, 0.0), template, (1.0, 1.0, 1.0))
    buf.add_instance((5.0, 0.0, 0.0), template, (1.0, 1.0, 1.0))
    _v, _n, _c, idxs = buf.to_arrays()
    assert buf.vertex_offset == 6
    assert idxs.tolist() == [0, 1, 2, 3, 4, 5]


def test_pnc_buffer_add_instance_scale() -> None:
    buf = PNCBuffer()
    template = MeshArrays(
        positions=[[1.0, 0.0, 0.0]],
        normals=[[1.0, 0.0, 0.0]],
        indices=[0],
    )
    buf.add_instance((10.0, 0.0, 0.0), template, (1.0, 0.0, 0.0), scale=2.0)
    verts, _n, _c, _i = buf.to_arrays()
    np.testing.assert_allclose(verts[0], (12.0, 0.0, 0.0))


def test_pnc_buffer_extend_offsets_indices() -> None:
    buf = PNCBuffer()
    buf.extend(
        positions=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
        normals=[[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        colors=[(1.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
        indices=[0, 1],
    )
    buf.extend(
        positions=[[2.0, 0.0, 0.0], [3.0, 0.0, 0.0]],
        normals=[[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        colors=[(0.0, 1.0, 0.0), (0.0, 1.0, 0.0)],
        indices=[0, 1],
    )
    _v, _n, _c, idxs = buf.to_arrays()
    assert idxs.tolist() == [0, 1, 2, 3]


def test_pnc_buffer_to_mesh_data() -> None:
    """Accumulated arrays become a MeshData with matching vertex counts."""
    from picogl.renderer.meshdata import MeshData

    buf = PNCBuffer()
    buf.extend(
        positions=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        normals=[[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        colors=[(1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
        indices=[0, 1, 2],
    )
    mesh = buf.to_mesh_data()
    assert isinstance(mesh, MeshData)
    assert mesh.vertices.shape[0] == 3
    assert mesh.indices.size == 3


def test_pnc_buffer_instances_unit_sphere_mesh() -> None:
    """Sphere template stays a geometry producer; PNCBuffer instances it."""
    sphere = unit_sphere_mesh(radius=0.2, slices=4, stacks=4)
    buf = PNCBuffer()
    buf.add_instance((0.0, 0.0, 0.0), sphere, (1.0, 0.0, 0.0))
    buf.add_instance((5.0, 0.0, 0.0), sphere, (0.0, 1.0, 0.0))
    verts, norms, cols, idxs = buf.to_arrays()
    n_verts = sphere.positions.shape[0]
    n_idx = int(sphere.indices.size)
    assert verts.shape == (2 * n_verts, 3)
    np.testing.assert_allclose(verts[:n_verts], sphere.positions)
    np.testing.assert_allclose(
        verts[n_verts:], sphere.positions + np.array([5.0, 0.0, 0.0], dtype=np.float32)
    )
    np.testing.assert_allclose(norms, np.tile(sphere.normals, (2, 1)))
    np.testing.assert_allclose(
        cols[:n_verts], np.broadcast_to((1.0, 0.0, 0.0), (n_verts, 3))
    )
    np.testing.assert_allclose(
        cols[n_verts:], np.broadcast_to((0.0, 1.0, 0.0), (n_verts, 3))
    )
    np.testing.assert_array_equal(idxs[n_idx:], sphere.indices + n_verts)
