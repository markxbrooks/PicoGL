"""Tests for molecular mesh data builders."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from picogl.backend.gl.enums import GLDrawMode
from picogl.core.geometry.sphere import unit_sphere_mesh
from picogl.renderer.molecular import AtomGeometry, AtomsMesh, BondGeometry, BondsMesh


@dataclass
class _Atom:
    x: float
    y: float
    z: float
    chain_id: str


def test_unit_sphere_mesh_counts() -> None:
    vertices, normals, indices = unit_sphere_mesh(radius=0.2, slices=16, stacks=16)
    assert vertices.shape == (17 * 17, 3)
    assert normals.shape == vertices.shape
    assert indices.size == 16 * 16 * 6


def test_atoms_mesh_single_atom_counts() -> None:
    atom = _Atom(1.0, 2.0, 3.0, "A")
    mesh = AtomsMesh([atom], radius=0.2, slices=16, stacks=16)
    data = mesh.to_mesh_data()

    template_vertices, _, template_indices = unit_sphere_mesh(0.2, 16, 16)
    assert data.vertices.shape[0] == template_vertices.shape[0]
    assert data.normals.shape[0] == template_vertices.shape[0]
    assert data.colors.shape[0] == template_vertices.shape[0]
    assert data.indices.size == template_indices.size
    assert data.vertices[0, 0] == pytest.approx(1.0 + template_vertices[0, 0])
    assert mesh.draw_mode == GLDrawMode.TRIANGLES


@dataclass
class _AtomCoords:
    coords: tuple[float, float, float]
    chain_id: str


def test_atoms_mesh_accepts_coords_attribute() -> None:
    """MoLib Atom3D-style objects expose coords, not x/y/z."""
    atom = _AtomCoords((1.0, 2.0, 3.0), "A")
    data = AtomsMesh([atom], radius=0.2, slices=4, stacks=4).to_mesh_data()
    template_vertices, _, _ = unit_sphere_mesh(0.2, 4, 4)
    assert data.vertices[0, 0] == pytest.approx(1.0 + template_vertices[0, 0])


def test_atoms_mesh_color_fn_receives_atom() -> None:
    atom = _Atom(0.0, 0.0, 0.0, "X")
    seen: list[object] = []

    def color_fn(a: object) -> tuple[float, float, float]:
        seen.append(a)
        return (0.1, 0.2, 0.3)

    data = AtomsMesh(
        [atom], color_fn=color_fn, radius=0.2, slices=4, stacks=4
    ).to_mesh_data()
    assert seen == [atom]
    assert data.colors.shape[0] == data.vertices.shape[0]
    np.testing.assert_allclose(data.colors[0], (0.1, 0.2, 0.3))


def test_bonds_mesh_single_bond() -> None:
    atom1 = _Atom(0.0, 0.0, 0.0, "A")
    atom2 = _Atom(1.0, 0.0, 0.0, "A")
    mesh = BondsMesh([(atom1, atom2)])
    data = mesh.to_mesh_data()

    segments = 8
    assert data.vertices.shape == (2 * segments, 3)
    assert data.normals.shape == (2 * segments, 3)
    assert data.colors.shape == (2 * segments, 3)
    assert data.indices.size == 6 * segments
    assert mesh.draw_mode == GLDrawMode.TRIANGLES


def test_bonds_mesh_cylinder_normals_perpendicular_to_axis() -> None:
    atom1 = _Atom(0.0, 0.0, 0.0, "A")
    atom2 = _Atom(1.0, 0.0, 0.0, "A")
    data = BondsMesh([(atom1, atom2)], segments=12).to_mesh_data()

    full_rings = np.reshape(data.vertices, (-1, 2, 3))
    assert np.allclose(full_rings[:, 0, 0], 0.0)
    assert np.allclose(full_rings[:, 1, 0], 1.0)
    assert np.allclose(data.normals[:, 0], 0.0)
    radial = np.linalg.norm(data.vertices[:, 1:], axis=1)
    assert np.allclose(radial, 0.06)


def test_bonds_mesh_custom_radius_and_color_fn() -> None:
    atom1 = _Atom(0.0, 0.0, 0.0, "A")
    atom2 = _Atom(1.0, 1.0, 1.0, "A")
    data = BondsMesh(
        [(atom1, atom2)],
        radius=0.3,
        segments=4,
        color_fn=lambda _chain: (1.0, 0.0, 0.0),
    ).to_mesh_data()

    assert data.vertices.shape == (8, 3)
    assert data.indices.size == 24
    np.testing.assert_allclose(data.colors[0], (1.0, 0.0, 0.0))
    start = np.array([0.0, 0.0, 0.0])
    end = np.array([1.0, 1.0, 1.0])
    bottom_ring = data.vertices[0::2]
    top_ring = data.vertices[1::2]
    np.testing.assert_allclose(
        np.linalg.norm(bottom_ring - start, axis=1), 0.3, rtol=1e-6
    )
    np.testing.assert_allclose(np.linalg.norm(top_ring - end, axis=1), 0.3, rtol=1e-6)


def test_atoms_mesh_custom_geometry() -> None:
    atom = _Atom(0.0, 0.0, 0.0, "A")
    geometry = AtomGeometry(radius=0.4, slices=4, stacks=4)
    data = AtomsMesh([atom], geometry=geometry).to_mesh_data()
    assert data.vertices.shape[0] == geometry.vertices_per_item
    assert data.draw_info.elements_per_item == geometry.elements_per_item
    assert data.draw_info.vertices_per_item == geometry.vertices_per_item


def test_bonds_mesh_custom_geometry() -> None:
    atom1 = _Atom(0.0, 0.0, 0.0, "A")
    atom2 = _Atom(1.0, 0.0, 0.0, "A")
    geometry = BondGeometry(radius=0.2, segments=6)
    data = BondsMesh([(atom1, atom2)], geometry=geometry).to_mesh_data()
    assert data.vertices.shape == (geometry.vertices_per_item, 3)
    assert data.indices.size == geometry.elements_per_item
    assert data.draw_info.elements_per_item == geometry.elements_per_item


def test_atoms_mesh_empty_uses_geometry_draw_info() -> None:
    geometry = AtomGeometry(slices=8, stacks=8)
    data = AtomsMesh([], geometry=geometry).to_mesh_data()
    assert data.vertices.shape[0] == 0
    assert data.draw_info.vertices_per_item == geometry.vertices_per_item
    assert data.draw_info.elements_per_item == geometry.elements_per_item


def test_to_legacy_glmesh_without_upload() -> None:
    atom = _Atom(0.0, 0.0, 0.0, "B")
    mesh = AtomsMesh([atom])
    legacy = mesh.to_legacy_glmesh(upload=False)
    assert legacy.vao is None


def test_to_glmesh_without_upload() -> None:
    atom = _Atom(0.0, 0.0, 0.0, "A")
    mesh = AtomsMesh([atom])
    modern = mesh.to_glmesh(upload=False)
    assert modern.vao is None
