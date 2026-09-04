"""Sphere-instanced atom mesh for molecular visualization."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from picogl.backend.gl.enums import GLDrawMode
from picogl.core.geometry.sphere import unit_sphere_mesh
from picogl.renderer.meshdata import MeshData
from picogl.renderer.molecular.base import MolecularMesh
from picogl.renderer.molecular.colors import chain_rgb


def atom_to_vertex(atom, vertex: list) -> list[Any]:
    """add atom coords to vertex"""
    return [
        vertex[0] + atom.x,
        vertex[1] + atom.y,
        vertex[2] + atom.z,
    ]


def add_atom_to_vertices(atom_vertices: list[list[float]], atom, vertex):
    """add atom to vertices"""
    atom_vertices.append(atom_to_vertex(atom, vertex))


class AtomsMesh(MolecularMesh):
    """
    Build triangle meshes by instancing a sphere template at each atom position.

    Atoms must expose ``x``, ``y``, ``z``, and ``chain_id`` attributes.
    """

    draw_mode = GLDrawMode.TRIANGLES

    def __init__(
        self,
        atoms: Sequence[Any],
        *,
        color_fn: Callable[[str], tuple[float, float, float]] = chain_rgb,
        radius: float = 0.2,
        slices: int = 16,
        stacks: int = 16,
    ) -> None:
        super().__init__()
        self.atoms = atoms
        self.color_fn = color_fn
        self.radius = radius
        self.slices = slices
        self.stacks = stacks

    def build_mesh_data(self) -> MeshData:
        """Instanciate sphere geometry at each atom and assign chain colors."""
        if not self.atoms:
            return MeshData.from_raw(
                vertices=np.zeros((0, 3), dtype=np.float32),
                indices=np.zeros((0,), dtype=np.uint32),
            )

        template_vertices, template_normals, template_indices = unit_sphere_mesh(
            self.radius,
            self.slices,
            self.stacks,
        )
        template_vertex_count = len(template_vertices)

        atom_vertices: list[list[float]] = []
        atom_normals: list[list[float]] = []
        atom_colors: list[tuple[float, float, float]] = []
        atom_indices: list[int] = []
        vertex_offset = 0

        for atom in self.atoms:
            color = self.color_fn(atom.chain_id)
            for vertex in template_vertices:
                add_atom_to_vertices(atom_vertices, atom, vertex)
                atom_colors.append(color)
            atom_normals.extend(template_normals.tolist())
            for idx in template_indices:
                atom_indices.append(int(idx) + vertex_offset)
            vertex_offset += template_vertex_count

        return MeshData.from_raw(
            vertices=np.array(atom_vertices, dtype=np.float32),
            normals=np.array(atom_normals, dtype=np.float32),
            colors=np.array(atom_colors, dtype=np.float32),
            indices=np.array(atom_indices, dtype=np.uint32),
        )
