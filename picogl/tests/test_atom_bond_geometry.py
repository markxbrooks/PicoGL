"""Tests for AtomGeometry and BondGeometry producers."""

from __future__ import annotations

import numpy as np

from picogl.core.geometry.sphere import unit_sphere_mesh
from picogl.renderer.molecular.atom_geometry import AtomGeometry
from picogl.renderer.molecular.bond_geometry import BondGeometry


def test_atom_geometry_counts_match_unit_sphere() -> None:
    geometry = AtomGeometry(radius=0.2, slices=16, stacks=16)
    vertices, _normals, indices = unit_sphere_mesh(0.2, 16, 16)
    data = geometry.build()
    built = np.asarray(data.vertices, dtype=np.float32).reshape(-1, 3)
    assert geometry.vertices_per_item == 17 * 17
    assert geometry.elements_per_item == 16 * 16 * 6
    assert built.shape[0] == geometry.vertices_per_item
    assert np.asarray(data.indices).size == geometry.elements_per_item
    np.testing.assert_allclose(built, vertices)


def test_bond_geometry_open_cylinder_topology() -> None:
    geometry = BondGeometry(radius=0.5, segments=4)
    data = geometry.build((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    verts = np.asarray(data.vertices, dtype=np.float32).reshape(-1, 3)
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
    verts = np.asarray(data.vertices, dtype=np.float32).reshape(-1, 3)
    assert verts.shape[0] == 0
    assert np.asarray(data.indices).size == 0


def test_bond_geometry_radial_normals_unit_length() -> None:
    data = BondGeometry(segments=12).build((0.0, 0.0, 0.0), (0.0, 0.0, 2.0))
    norms = np.asarray(data.normals, dtype=np.float32).reshape(-1, 3)
    np.testing.assert_allclose(np.linalg.norm(norms, axis=1), 1.0)
    np.testing.assert_allclose(norms[:, 2], 0.0)
