"""Tests for PNCPart MeshData / MeshArrays helpers."""

from __future__ import annotations

import numpy as np
from picogl.renderer.mesh_arrays import MeshArrays
from picogl.renderer.mesh_builder import mesh_part_from_pnc
from picogl.renderer.meshdata import MeshData, PNCPart


def _sample_pnc() -> PNCPart:
    positions = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=np.float32)
    normals = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    colors = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)
    return positions, normals, colors


def test_meshdata_from_pnc_and_as_pnc_roundtrip() -> None:
    part = _sample_pnc()
    mesh = MeshData.from_pnc(part)
    out = mesh.as_pnc()
    np.testing.assert_allclose(out[0], part[0])
    np.testing.assert_allclose(out[1], part[1])
    np.testing.assert_allclose(out[2], part[2])


def test_meshdata_with_pnc_colors_preserves_positions() -> None:
    mesh = MeshData.from_pnc(_sample_pnc())
    new_colors = np.array([[0.2, 0.3, 0.4], [0.5, 0.6, 0.7]], dtype=np.float32)
    painted = mesh.with_pnc_colors(new_colors)
    np.testing.assert_allclose(painted.as_pnc()[0], mesh.as_pnc()[0])
    np.testing.assert_allclose(painted.as_pnc()[2], new_colors)


def test_mesh_arrays_from_pnc() -> None:
    part = _sample_pnc()
    arrays = MeshArrays.from_pnc(part)
    np.testing.assert_allclose(arrays.as_pnc()[0], part[0])


def test_mesh_part_from_pnc_keeps_attribute_order() -> None:
    part = _sample_pnc()
    faces = np.array([[0, 1, 0]], dtype=np.uint32)
    mesh_part = mesh_part_from_pnc(part, faces)
    assert mesh_part[0] is part[0]
    assert mesh_part[1] is faces
    assert mesh_part[2] is part[1]
    assert mesh_part[3] is part[2]
