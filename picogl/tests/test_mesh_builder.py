"""Tests for indexed MeshBuilder."""

from __future__ import annotations

import numpy as np
from picogl.renderer.mesh_builder import (
    MeshBuilder,
    solid_color_mesh_part,
    stack_mesh_parts,
)


def _part(n_vertices: int, face_offset: int = 0):
    vertices = np.arange(n_vertices * 3, dtype=np.float32).reshape(n_vertices, 3)
    faces = np.array([[0, 1, 2]], dtype=np.uint32) + face_offset
    normals = np.ones((n_vertices, 3), dtype=np.float32)
    colors = np.full((n_vertices, 3), 0.5, dtype=np.float32)
    return vertices, faces, normals, colors


def test_mesh_builder_offsets_second_part_faces() -> None:
    with MeshBuilder() as builder:
        builder.add_part(_part(3))
        builder.add_part(_part(4))
        stacked = builder.build()
    assert stacked is not None
    vertices, faces, normals, colors = stacked
    assert len(vertices) == 7
    assert len(normals) == 7
    assert len(colors) == 7
    np.testing.assert_array_equal(faces[0], np.array([0, 1, 2], dtype=np.uint32))
    np.testing.assert_array_equal(faces[1], np.array([3, 4, 5], dtype=np.uint32))


def test_mesh_builder_skips_none_and_empty() -> None:
    empty = (
        np.zeros((0, 3), dtype=np.float32),
        np.zeros((0, 3), dtype=np.uint32),
        np.zeros((0, 3), dtype=np.float32),
        np.zeros((0, 3), dtype=np.float32),
    )
    builder = MeshBuilder()
    builder.add_part(None)
    builder.add_part(empty)
    builder.add_part(_part(3))
    mesh = builder.mesh_data()
    assert mesh is not None
    assert len(mesh.vertices) == 3


def test_stack_mesh_parts_all_empty_returns_none() -> None:
    assert stack_mesh_parts((None, None)) is None


def test_solid_color_mesh_part_tiles_rgb() -> None:
    vertices = np.zeros((4, 3), dtype=np.float32)
    faces = np.array([[0, 1, 2]], dtype=np.uint32)
    normals = np.ones((4, 3), dtype=np.float32)
    part = solid_color_mesh_part(vertices, faces, normals, (0.1, 0.2, 0.3))
    vtx, fcs, nrms, cols = part
    assert vtx is vertices
    assert fcs is faces
    assert nrms is normals
    assert cols.shape == (4, 3)
    np.testing.assert_allclose(cols[0], [0.1, 0.2, 0.3])
    np.testing.assert_allclose(cols[3], [0.1, 0.2, 0.3])


def test_mesh_builder_accepts_flat_index_buffer() -> None:
    vertices = np.zeros((3, 3), dtype=np.float32)
    faces = np.array([0, 1, 2], dtype=np.uint32)
    normals = np.ones((3, 3), dtype=np.float32)
    colors = np.full((3, 3), 0.5, dtype=np.float32)
    builder = MeshBuilder()
    builder.add_part((vertices, faces, normals, colors))
    builder.add_part((vertices, faces, normals, colors))
    stacked = builder.build()
    assert stacked is not None
    _vertices, out_faces, _normals, _colors = stacked
    assert out_faces.ndim == 1
    np.testing.assert_array_equal(
        out_faces, np.array([0, 1, 2, 3, 4, 5], dtype=np.uint32)
    )
