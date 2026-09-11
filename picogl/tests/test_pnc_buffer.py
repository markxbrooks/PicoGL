"""Tests for PNCBuffer mesh assembly."""

from __future__ import annotations

import numpy as np

from picogl.renderer.molecular.pnc_buffer import PNCBuffer


def test_pnc_buffer_add_instance_offsets_indices() -> None:
    buf = PNCBuffer()
    template_v = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]
    template_n = [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]]
    template_i = [0, 1]
    buf.add_instance(
        (10.0, 0.0, 0.0), template_v, template_n, template_i, (1.0, 0.0, 0.0)
    )
    buf.add_instance(
        (0.0, 20.0, 0.0), template_v, template_n, template_i, (0.0, 1.0, 0.0)
    )
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
    vertices = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    normals = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    indices = np.array([0, 1, 2], dtype=np.uint32)
    buf.add_instance((0.0, 0.0, 0.0), vertices, normals, indices, (1.0, 1.0, 1.0))
    buf.add_instance((5.0, 0.0, 0.0), vertices, normals, indices, (1.0, 1.0, 1.0))
    _v, _n, _c, idxs = buf.to_arrays()
    assert buf.vertex_offset == 6
    assert idxs.tolist() == [0, 1, 2, 3, 4, 5]


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


def test_molecular_package_import_is_not_circular() -> None:
    """Package exports must load without a BondsMesh circular import."""
    from picogl.renderer.molecular import AtomsMesh, BondsMesh, PNCBuffer, chain_rgb

    assert callable(chain_rgb)
    assert AtomsMesh is not None
    assert BondsMesh is not None
    assert PNCBuffer is not None
