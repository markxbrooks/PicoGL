"""Tests for CPU-side MeshArrays."""

from __future__ import annotations

import numpy as np
import pytest

from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.mesh_arrays import MeshArrays
from picogl.renderer.meshdata import MeshData


def test_mesh_arrays_casts_to_float32_and_uint32() -> None:
    mesh = MeshArrays(
        positions=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float64),
        normals=np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]], dtype=np.float64),
        colors=np.array([0.1, 0.2, 0.3], dtype=np.float64),
        indices=np.array([0, 1, 0], dtype=np.int64),
    )
    assert mesh.positions.dtype == np.float32
    assert mesh.normals.dtype == np.float32
    assert mesh.colors is not None
    assert mesh.colors.dtype == np.float32
    assert mesh.colors.shape == (2, 3)
    assert mesh.indices is not None
    assert mesh.indices.dtype == np.uint32
    assert mesh.indexed is True
    np.testing.assert_allclose(mesh.colors[0], [0.1, 0.2, 0.3])
    np.testing.assert_allclose(mesh.colors[1], [0.1, 0.2, 0.3])


def test_mesh_arrays_rejects_bad_shapes() -> None:
    positions = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)
    normals = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    with pytest.raises(ValueError, match="positions"):
        MeshArrays(positions=np.array([1.0, 0.0, 0.0]), normals=normals)
    with pytest.raises(ValueError, match="normals"):
        MeshArrays(positions=positions, normals=np.array([[0.0, 0.0, 1.0]]))
    with pytest.raises(ValueError, match="colors"):
        MeshArrays(
            positions=positions,
            normals=normals,
            colors=np.array([[1.0, 0.0, 0.0]]),
        )
    with pytest.raises(ValueError, match="indices"):
        MeshArrays(
            positions=positions,
            normals=normals,
            indices=np.array([[0, 1]]),
        )


def test_mesh_arrays_rejects_out_of_range_indices() -> None:
    positions = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)
    normals = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    with pytest.raises(ValueError, match="out-of-range"):
        MeshArrays(
            positions=positions,
            normals=normals,
            indices=np.array([0, 2], dtype=np.uint32),
        )


def test_mesh_arrays_with_colors_returns_new_instance() -> None:
    mesh = MeshArrays(
        positions=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32),
        normals=np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]], dtype=np.float32),
        indices=np.array([0, 1, 0], dtype=np.uint32),
    )
    colors = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)
    colored = mesh.with_colors(colors)
    assert mesh.colors is None
    np.testing.assert_allclose(colored.colors, colors)
    np.testing.assert_array_equal(colored.positions, mesh.positions)
    np.testing.assert_array_equal(colored.indices, mesh.indices)


def test_mesh_arrays_as_meshdata_defaults_to_triangles() -> None:
    mesh = MeshArrays(
        positions=np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            dtype=np.float32,
        ),
        normals=np.array(
            [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        ),
        colors=np.array(
            [[1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
            dtype=np.float32,
        ),
    )
    data = mesh.as_meshdata()
    assert isinstance(data, MeshData)
    assert data.draw_info.mode == GLDrawMode.TRIANGLES
    assert data.draw_info.indexed is False
    np.testing.assert_allclose(data.vertices, mesh.positions)

    indexed = MeshArrays(
        positions=mesh.positions,
        normals=mesh.normals,
        colors=mesh.colors,
        indices=np.array([0, 1, 2], dtype=np.uint32),
    ).as_meshdata()
    assert indexed.draw_info.indexed is True
    assert indexed.draw_info.mode == GLDrawMode.TRIANGLES
