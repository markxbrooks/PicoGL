"""Tests for SphereGeometrySpec and SphereMesh."""

from __future__ import annotations

import numpy as np

from picogl.core.geometry.sphere import SphereGeometrySpec, SphereMesh, sphere_mesh
from picogl.renderer.mesh_arrays import MeshArrays


def test_sphere_mesh_build_matches_sphere_mesh() -> None:
    spec = SphereGeometrySpec(radius=0.5, slices=8, stacks=6)
    mesh = SphereMesh(spec)
    built = mesh.build()
    expected = sphere_mesh(radius=0.5, slices=8, stacks=6)
    assert isinstance(built, MeshArrays)
    assert built.colors is None
    np.testing.assert_allclose(built.positions, expected.positions)
    np.testing.assert_allclose(built.normals, expected.normals)
    np.testing.assert_array_equal(built.indices, expected.indices)


def test_sphere_mesh_counts_follow_slices_and_stacks() -> None:
    spec = SphereGeometrySpec(slices=4, stacks=3)
    mesh = SphereMesh(spec)
    built = mesh.build()
    assert mesh.vertices_per_item == 4 * 5
    assert mesh.elements_per_item == 6 * 3 * 4
    assert built.positions.shape[0] == mesh.vertices_per_item
    assert built.indices is not None
    assert built.indices.size == mesh.elements_per_item
