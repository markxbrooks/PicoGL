"""Tests for PNCBuffer mesh assembly."""

from __future__ import annotations

import numpy as np
import pytest
from picogl.core.geometry.sphere import sphere_mesh
from picogl.renderer.mesh_arrays import MeshArrays
from picogl.renderer.meshdata import MeshData
from picogl.renderer.molecular.pnc_buffer import PNCBuffer


def _line_template() -> MeshArrays:
    return MeshArrays(
        positions=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
        normals=[[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        indices=[0, 1],
    )


def test_pnc_buffer_add_instance_offsets_indices() -> None:
    buf = PNCBuffer()
    mesh = _line_template()
    buf.add_instance(mesh, (10.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    buf.add_instance(mesh, (0.0, 20.0, 0.0), (0.0, 1.0, 0.0))
    combined = buf.to_mesh_arrays()
    assert isinstance(combined, MeshArrays)
    assert combined.positions.shape == (4, 3)
    assert combined.normals.shape == (4, 3)
    assert combined.colors is not None
    assert combined.colors.shape == (4, 3)
    np.testing.assert_allclose(combined.positions[0], (10.0, 0.0, 0.0))
    np.testing.assert_allclose(combined.positions[2], (0.0, 20.0, 0.0))
    assert combined.indices is not None
    assert combined.indices.tolist() == [0, 1, 2, 3]
    np.testing.assert_allclose(combined.colors[0], (1.0, 0.0, 0.0))
    np.testing.assert_allclose(combined.colors[2], (0.0, 1.0, 0.0))


def test_pnc_buffer_add_instance_uses_template_length() -> None:
    buf = PNCBuffer()
    mesh = MeshArrays(
        positions=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        normals=[[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        indices=[0, 1, 2],
    )
    buf.add_instance(mesh, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0))
    buf.add_instance(mesh, (5.0, 0.0, 0.0), (1.0, 1.0, 1.0))
    combined = buf.to_mesh_arrays()
    assert buf.vertex_offset == 6
    assert combined.indices is not None
    assert combined.indices.tolist() == [0, 1, 2, 3, 4, 5]


def test_pnc_buffer_add_instance_scale() -> None:
    buf = PNCBuffer()
    mesh = MeshArrays(
        positions=[[1.0, 0.0, 0.0]],
        normals=[[1.0, 0.0, 0.0]],
        indices=[0],
    )
    buf.add_instance(mesh, (10.0, 0.0, 0.0), (1.0, 0.0, 0.0), scale=2.0)
    combined = buf.to_mesh_arrays()
    np.testing.assert_allclose(combined.positions[0], (12.0, 0.0, 0.0))


def test_pnc_buffer_extend_offsets_indices() -> None:
    buf = PNCBuffer()
    buf.extend(
        MeshArrays(
            positions=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
            normals=[[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
            colors=[(1.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
            indices=[0, 1],
        )
    )
    buf.extend(
        MeshArrays(
            positions=[[2.0, 0.0, 0.0], [3.0, 0.0, 0.0]],
            normals=[[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
            colors=[(0.0, 1.0, 0.0), (0.0, 1.0, 0.0)],
            indices=[0, 1],
        )
    )
    combined = buf.to_mesh_arrays()
    assert combined.indices is not None
    assert combined.indices.tolist() == [0, 1, 2, 3]


def test_pnc_buffer_extend_requires_colors() -> None:
    buf = PNCBuffer()
    mesh = MeshArrays(
        positions=[[0.0, 0.0, 0.0]],
        normals=[[0.0, 0.0, 1.0]],
        indices=[0],
    )
    with pytest.raises(ValueError, match="color"):
        buf.extend(mesh)
    buf.extend(mesh, color=(1.0, 0.0, 0.0))
    combined = buf.to_mesh_arrays()
    assert combined.colors is not None
    np.testing.assert_allclose(combined.colors[0], (1.0, 0.0, 0.0))


def test_pnc_buffer_to_mesh_data() -> None:
    """Accumulated arrays become MeshData via as_meshdata()."""
    buf = PNCBuffer()
    buf.extend(
        MeshArrays(
            positions=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            normals=[[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
            colors=[(1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
            indices=[0, 1, 2],
        )
    )
    arrays = buf.to_mesh_arrays()
    mesh = buf.to_mesh_data()
    assert isinstance(arrays, MeshArrays)
    assert isinstance(mesh, MeshData)
    assert mesh.vertices.shape[0] == 3
    assert mesh.indices.size == 3
    np.testing.assert_allclose(mesh.vertices, arrays.positions)


def test_pnc_buffer_add_instances_two_translations() -> None:
    buf = PNCBuffer()
    mesh = _line_template()
    buf.add_instances(
        mesh,
        np.array([[10.0, 0.0, 0.0], [0.0, 20.0, 0.0]], dtype=np.float32),
        np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32),
    )
    combined = buf.to_mesh_arrays()
    assert combined.positions.shape == (4, 3)
    np.testing.assert_allclose(combined.positions[0], (10.0, 0.0, 0.0))
    np.testing.assert_allclose(combined.positions[2], (0.0, 20.0, 0.0))
    assert combined.indices is not None
    assert combined.indices.tolist() == [0, 1, 2, 3]
    assert combined.colors is not None
    np.testing.assert_allclose(combined.colors[0], (1.0, 0.0, 0.0))
    np.testing.assert_allclose(combined.colors[2], (0.0, 1.0, 0.0))


def test_pnc_buffer_add_instances_scales() -> None:
    buf = PNCBuffer()
    mesh = MeshArrays(
        positions=[[1.0, 0.0, 0.0]],
        normals=[[1.0, 0.0, 0.0]],
        indices=[0],
    )
    buf.add_instances(
        mesh,
        np.array([[10.0, 0.0, 0.0], [0.0, 0.0, 0.0]], dtype=np.float32),
        np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32),
        scales=np.array([2.0, 0.5], dtype=np.float32),
    )
    combined = buf.to_mesh_arrays()
    np.testing.assert_allclose(combined.positions[0], (12.0, 0.0, 0.0))
    np.testing.assert_allclose(combined.positions[1], (0.5, 0.0, 0.0))


def test_pnc_buffer_add_instances_empty_is_noop() -> None:
    buf = PNCBuffer()
    buf.add_instances(
        _line_template(),
        np.zeros((0, 3), dtype=np.float32),
        np.zeros((0, 3), dtype=np.float32),
    )
    combined = buf.to_mesh_arrays()
    assert combined.positions.shape == (0, 3)
    assert buf.vertex_offset == 0


def test_pnc_buffer_instances_unit_sphere_mesh() -> None:
    """Sphere template stays a geometry producer; PNCBuffer instances it."""
    sphere = sphere_mesh(radius=0.2, slices=4, stacks=4)
    buf = PNCBuffer()
    buf.add_instance(sphere, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    buf.add_instance(sphere, (5.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    combined = buf.to_mesh_arrays()
    n_verts = sphere.positions.shape[0]
    n_idx = int(sphere.indices.size)
    assert combined.positions.shape == (2 * n_verts, 3)
    np.testing.assert_allclose(combined.positions[:n_verts], sphere.positions)
    np.testing.assert_allclose(
        combined.positions[n_verts:],
        sphere.positions + np.array([5.0, 0.0, 0.0], dtype=np.float32),
    )
    np.testing.assert_allclose(combined.normals, np.tile(sphere.normals, (2, 1)))
    assert combined.colors is not None
    np.testing.assert_allclose(
        combined.colors[:n_verts], np.broadcast_to((1.0, 0.0, 0.0), (n_verts, 3))
    )
    np.testing.assert_allclose(
        combined.colors[n_verts:], np.broadcast_to((0.0, 1.0, 0.0), (n_verts, 3))
    )
    assert combined.indices is not None
    np.testing.assert_array_equal(combined.indices[n_idx:], sphere.indices + n_verts)
