"""Tests for molecular mesh data builders."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest
from picogl.backend.gl.enums import GLDrawMode
from picogl.core.geometry.sphere import unit_sphere_mesh
from picogl.renderer.molecular import AtomsMesh, BondsMesh


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


def test_bonds_mesh_single_bond() -> None:
    atom1 = _Atom(0.0, 0.0, 0.0, "A")
    atom2 = _Atom(1.0, 0.0, 0.0, "A")
    mesh = BondsMesh([(atom1, atom2)])
    data = mesh.to_mesh_data()

    assert data.vertices.shape == (2, 3)
    assert data.colors.shape == (2, 3)
    assert data.indices.tolist() == [0, 1]
    assert mesh.draw_mode == GLDrawMode.LINES


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
