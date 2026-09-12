"""Tests for molecular mesh data builders."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from picogl.backend.gl.enums import GLDrawMode
from picogl.core.geometry.sphere import unit_sphere_mesh
from picogl.renderer.molecular import AtomGeometry, BondGeometry
from molib.gl.mesh.atom.sphere import AtomSpheresMesh
from molib.gl.mesh.bond.cylinder import BondCylindersMesh


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
    mesh = AtomSpheresMesh([atom], radius=0.2, slices=16, stacks=16)
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
    data = AtomSpheresMesh([atom], radius=0.2, slices=4, stacks=4).to_mesh_data()
    template_vertices, _, _ = unit_sphere_mesh(0.2, 4, 4)
    assert data.vertices[0, 0] == pytest.approx(1.0 + template_vertices[0, 0])


def test_atoms_mesh_color_fn_receives_atom() -> None:
    atom = _Atom(0.0, 0.0, 0.0, "X")
    seen: list[object] = []

    def color_fn(a: object) -> tuple[float, float, float]:
        seen.append(a)
        return (0.1, 0.2, 0.3)

    data = AtomSpheresMesh(
        [atom], color_fn=color_fn, radius=0.2, slices=4, stacks=4
    ).to_mesh_data()
    assert seen == [atom]
    assert data.colors.shape[0] == data.vertices.shape[0]
    np.testing.assert_allclose(data.colors[0], (0.1, 0.2, 0.3))


def test_atoms_mesh_two_atoms_vectorized_expand() -> None:
    """Two atoms expand one template: tiled normals, repeated colors, offset EBO."""
    atom_a = _Atom(0.0, 0.0, 0.0, "A")
    atom_b = _Atom(5.0, 0.0, 0.0, "B")

    def color_fn(atom: _Atom) -> tuple[float, float, float]:
        return (1.0, 0.0, 0.0) if atom.chain_id == "A" else (0.0, 1.0, 0.0)

    data = AtomSpheresMesh(
        [atom_a, atom_b],
        color_fn=color_fn,
        radius=0.2,
        slices=4,
        stacks=4,
    ).to_mesh_data()

    template_vertices, template_normals, template_indices = unit_sphere_mesh(
        0.2, 4, 4
    )
    n_verts = template_vertices.shape[0]
    n_idx = int(template_indices.size)

    assert data.vertices.shape == (2 * n_verts, 3)
    assert data.normals.shape == (2 * n_verts, 3)
    assert data.colors.shape == (2 * n_verts, 3)
    assert data.indices.size == 2 * n_idx

    np.testing.assert_allclose(data.vertices[:n_verts], template_vertices)
    np.testing.assert_allclose(
        data.vertices[n_verts:], template_vertices + np.array([5.0, 0.0, 0.0])
    )
    np.testing.assert_allclose(
        data.normals, np.tile(template_normals, (2, 1))
    )
    np.testing.assert_allclose(
        data.colors[:n_verts], np.broadcast_to((1.0, 0.0, 0.0), (n_verts, 3))
    )
    np.testing.assert_allclose(
        data.colors[n_verts:], np.broadcast_to((0.0, 1.0, 0.0), (n_verts, 3))
    )
    np.testing.assert_array_equal(
        data.indices[n_idx:], np.asarray(template_indices) + n_verts
    )
    assert data.draw_info.vertices_per_item == n_verts
    assert data.draw_info.elements_per_item == n_idx


def test_atoms_mesh_default_color_fn_uses_chain_palette() -> None:
    """Omitting color_fn must not crash; colors follow make_chain_color_fn."""
    from molib.gl.mesh.atom.sphere import make_chain_color_fn

    atoms = [_Atom(0.0, 0.0, 0.0, "A"), _Atom(1.0, 0.0, 0.0, "B")]
    data = AtomSpheresMesh(atoms, radius=0.2, slices=4, stacks=4).to_mesh_data()
    expected_fn = make_chain_color_fn(["A", "B"])
    n_verts = data.vertices.shape[0] // 2
    np.testing.assert_allclose(data.colors[0], expected_fn(atoms[0]))
    np.testing.assert_allclose(data.colors[n_verts], expected_fn(atoms[1]))


def test_bonds_mesh_single_bond() -> None:
    atom1 = _Atom(0.0, 0.0, 0.0, "A")
    atom2 = _Atom(1.0, 0.0, 0.0, "A")
    mesh = BondCylindersMesh([(atom1, atom2)], color_fn=lambda _atom: (1.0, 0.0, 0.0))
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
    data = BondCylindersMesh(
        [(atom1, atom2)],
        segments=12,
        color_fn=lambda _atom: (1.0, 0.0, 0.0),
    ).to_mesh_data()

    full_rings = np.reshape(data.vertices, (-1, 2, 3))
    assert np.allclose(full_rings[:, 0, 0], 0.0)
    assert np.allclose(full_rings[:, 1, 0], 1.0)
    assert np.allclose(data.normals[:, 0], 0.0)
    radial = np.linalg.norm(data.vertices[:, 1:], axis=1)
    assert np.allclose(radial, 0.06)


def test_bonds_mesh_custom_radius_and_color_fn() -> None:
    atom1 = _Atom(0.0, 0.0, 0.0, "A")
    atom2 = _Atom(1.0, 1.0, 1.0, "A")
    data = BondCylindersMesh(
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
    data = AtomSpheresMesh([atom], geometry=geometry).to_mesh_data()
    assert data.vertices.shape[0] == geometry.vertices_per_item
    assert data.draw_info.elements_per_item == geometry.elements_per_item
    assert data.draw_info.vertices_per_item == geometry.vertices_per_item


def test_bonds_mesh_custom_geometry() -> None:
    atom1 = _Atom(0.0, 0.0, 0.0, "A")
    atom2 = _Atom(1.0, 0.0, 0.0, "A")
    geometry = BondGeometry(radius=0.2, segments=6)
    data = BondCylindersMesh(
        [(atom1, atom2)],
        geometry=geometry,
        color_fn=lambda _atom: (1.0, 0.0, 0.0),
    ).to_mesh_data()
    assert data.vertices.shape == (geometry.vertices_per_item, 3)
    assert data.indices.size == geometry.elements_per_item
    assert data.draw_info.elements_per_item == geometry.elements_per_item


def test_bonds_mesh_two_bonds_vectorized_expand() -> None:
    """Two shafts: doubled vertex count, per-shaft colors, offset EBO."""
    atom_a = _Atom(0.0, 0.0, 0.0, "A")
    atom_b = _Atom(1.0, 0.0, 0.0, "A")
    atom_c = _Atom(0.0, 2.0, 0.0, "B")
    atom_d = _Atom(0.0, 3.0, 0.0, "B")

    def color_fn(atom: _Atom) -> tuple[float, float, float]:
        return (1.0, 0.0, 0.0) if atom.chain_id == "A" else (0.0, 1.0, 0.0)

    data = BondCylindersMesh(
        [(atom_a, atom_b), (atom_c, atom_d)],
        color_fn=color_fn,
        segments=4,
    ).to_mesh_data()
    n_verts = 2 * 4
    n_idx = 6 * 4
    assert data.vertices.shape == (2 * n_verts, 3)
    assert data.colors.shape == (2 * n_verts, 3)
    assert data.indices.size == 2 * n_idx
    first = BondCylindersMesh([(atom_a, atom_b)], color_fn=color_fn, segments=4).to_mesh_data()
    np.testing.assert_allclose(data.vertices[:n_verts], first.vertices)
    np.testing.assert_allclose(
        data.colors[:n_verts], np.broadcast_to((1.0, 0.0, 0.0), (n_verts, 3))
    )
    np.testing.assert_allclose(
        data.colors[n_verts:], np.broadcast_to((0.0, 1.0, 0.0), (n_verts, 3))
    )
    np.testing.assert_array_equal(
        np.asarray(data.indices).ravel()[n_idx:],
        np.asarray(first.indices).ravel() + n_verts,
    )


def test_bonds_mesh_skips_zero_length_without_repeating_color() -> None:
    """A collapsed pair adds neither vertices nor a color block."""
    atom_a = _Atom(0.0, 0.0, 0.0, "A")
    atom_b = _Atom(1.0, 0.0, 0.0, "A")
    collapsed = _Atom(0.0, 0.0, 0.0, "B")
    data = BondCylindersMesh(
        [(atom_a, atom_a), (atom_a, atom_b), (collapsed, collapsed)],
        color_fn=lambda atom: (0.0, 0.0, 1.0) if atom.chain_id == "A" else (1.0, 0.0, 0.0),
        segments=4,
    ).to_mesh_data()
    n_verts = 2 * 4
    assert data.vertices.shape == (n_verts, 3)
    assert data.colors.shape == (n_verts, 3)
    np.testing.assert_allclose(
        data.colors, np.broadcast_to((0.0, 0.0, 1.0), (n_verts, 3))
    )


def test_atoms_mesh_empty_uses_geometry_draw_info() -> None:
    geometry = AtomGeometry(slices=8, stacks=8)
    data = AtomSpheresMesh([], geometry=geometry).to_mesh_data()
    assert data.vertices.shape[0] == 0
    assert data.draw_info.vertices_per_item == geometry.vertices_per_item
    assert data.draw_info.elements_per_item == geometry.elements_per_item


def test_to_legacy_glmesh_without_upload() -> None:
    atom = _Atom(0.0, 0.0, 0.0, "B")
    mesh = AtomSpheresMesh([atom])
    legacy = mesh.to_legacy_glmesh(upload=False)
    assert legacy.vao is None


def test_to_glmesh_without_upload() -> None:
    atom = _Atom(0.0, 0.0, 0.0, "A")
    mesh = AtomSpheresMesh([atom])
    modern = mesh.to_glmesh(upload=False)
    assert modern.vao is None
