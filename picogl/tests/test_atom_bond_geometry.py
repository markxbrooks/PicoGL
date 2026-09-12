"""Tests for AtomGeometry and BondGeometry producers."""

from __future__ import annotations

import numpy as np

from picogl.core.geometry.sphere import unit_sphere_mesh
from picogl.renderer.mesh_arrays import MeshArrays
from molib.gl.mesh.atom.sphere_geometry import AtomSphereGeometry
from picogl.renderer.molecular.bond_geometry import BondGeometry


def test_atom_geometry_counts_match_unit_sphere() -> None:
    geometry = AtomSphereGeometry(radius=0.2, slices=16, stacks=16)
    vertices, _normals, indices = unit_sphere_mesh(0.2, 16, 16)
    data = geometry.build()
    built = np.asarray(data.positions, dtype=np.float32).reshape(-1, 3)
    assert isinstance(data, MeshArrays)
    assert data.colors is None
    assert geometry.vertices_per_item == 17 * 17
    assert geometry.elements_per_item == 16 * 16 * 6
    assert built.shape[0] == geometry.vertices_per_item
    assert np.asarray(data.indices).size == geometry.elements_per_item
    np.testing.assert_allclose(built, vertices)


def test_bond_geometry_open_cylinder_topology() -> None:
    geometry = BondGeometry(radius=0.5, segments=4)
    data = geometry.build((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    verts = np.asarray(data.positions, dtype=np.float32).reshape(-1, 3)
    norms = np.asarray(data.normals, dtype=np.float32).reshape(-1, 3)
    idxs = np.asarray(data.indices).ravel().tolist()

    assert geometry.vertices_per_item == 8
    assert geometry.elements_per_item == 24
    assert verts.shape == (8, 3)
    assert norms.shape == (8, 3)
    assert idxs == [
        0,
        2,
        1,
        2,
        3,
        1,
        2,
        4,
        3,
        4,
        5,
        3,
        4,
        6,
        5,
        6,
        7,
        5,
        6,
        0,
        7,
        0,
        1,
        7,
    ]
    np.testing.assert_allclose(verts[0, 0], 0.0)
    np.testing.assert_allclose(verts[1, 0], 1.0)
    radial = np.linalg.norm(verts[:, 1:], axis=1)
    np.testing.assert_allclose(radial, 0.5)
    np.testing.assert_allclose(norms[0], [0.0, -1.0, 0.0])


def test_bond_geometry_zero_length_is_empty() -> None:
    data = BondGeometry().build((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    verts = np.asarray(data.positions, dtype=np.float32).reshape(-1, 3)
    assert verts.shape[0] == 0
    assert np.asarray(data.indices).size == 0


def test_bond_geometry_radial_normals_unit_length() -> None:
    data = BondGeometry(segments=12).build((0.0, 0.0, 0.0), (0.0, 0.0, 2.0))
    norms = np.asarray(data.normals, dtype=np.float32).reshape(-1, 3)
    np.testing.assert_allclose(np.linalg.norm(norms, axis=1), 1.0)
    np.testing.assert_allclose(norms[:, 2], 0.0)


def test_bond_geometry_build_many_matches_sequential_build() -> None:
    """Two finite bonds match concatenated single-bond ``build()`` results."""
    geometry = BondGeometry(radius=0.5, segments=4)
    starts = np.array([[0.0, 0.0, 0.0], [3.0, 0.0, 0.0]])
    ends = np.array([[1.0, 0.0, 0.0], [3.0, 2.0, 0.0]])
    mesh, valid = geometry.build_many(starts, ends)
    positions, normals, indices = mesh.positions, mesh.normals, mesh.indices
    assert np.all(valid)
    first = geometry.build(starts[0], ends[0])
    second = geometry.build(starts[1], ends[1])
    v0 = np.asarray(first.positions, dtype=np.float32).reshape(-1, 3)
    v1 = np.asarray(second.positions, dtype=np.float32).reshape(-1, 3)
    n0 = np.asarray(first.normals, dtype=np.float32).reshape(-1, 3)
    n1 = np.asarray(second.normals, dtype=np.float32).reshape(-1, 3)
    i0 = np.asarray(first.indices, dtype=np.uint32).ravel()
    i1 = np.asarray(second.indices, dtype=np.uint32).ravel()
    np.testing.assert_allclose(positions, np.concatenate([v0, v1]))
    np.testing.assert_allclose(normals, np.concatenate([n0, n1]))
    np.testing.assert_array_equal(
        indices, np.concatenate([i0, i1 + np.uint32(v0.shape[0])])
    )
    np.testing.assert_allclose(np.linalg.norm(normals, axis=1), 1.0)


def test_bond_geometry_build_many_drops_zero_length() -> None:
    """Mixed finite + zero-length input yields one cylinder."""
    geometry = BondGeometry(segments=8)
    starts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [5.0, 0.0, 0.0]])
    ends = np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [5.0, 0.0, 0.0]])
    mesh, valid = geometry.build_many(starts, ends)
    positions, indices = mesh.positions, mesh.indices
    np.testing.assert_array_equal(valid, [False, True, False])
    assert positions.shape[0] == geometry.vertices_per_item
    assert indices.size == geometry.elements_per_item
    solo = geometry.build(starts[1], ends[1])
    np.testing.assert_allclose(
        positions, np.asarray(solo.positions, dtype=np.float32).reshape(-1, 3)
    )
