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


def atom_xyz(atom: Any) -> tuple[float, float, float]:
    """Return ``(x, y, z)`` from ``atom.x/y/z`` or ``atom.coords`` (e.g. Atom3D)."""
    coords = getattr(atom, "coords", None)
    if coords is not None:
        return float(coords[0]), float(coords[1]), float(coords[2])
    return float(atom.x), float(atom.y), float(atom.z)


def atom_to_vertex(atom, vertex: list) -> list[Any]:
    """add atom coords to vertex"""
    x, y, z = atom_xyz(atom)
    return [
        vertex[0] + x,
        vertex[1] + y,
        vertex[2] + z,
    ]


def add_atom_to_vertices(atom_vertices: list[list[float]], atom, vertex):
    """add atom to vertices"""
    atom_vertices.append(atom_to_vertex(atom, vertex))


def _default_atom_color(atom: Any) -> tuple[float, float, float]:
    """Default color from atom ``chain_id`` (compatible with :func:`chain_rgb`)."""
    return chain_rgb(getattr(atom, "chain_id", ""))


class AtomsMesh(MolecularMesh):
    """
    Build triangle meshes by instancing a sphere template at each atom position.

    Atoms must expose either ``x``, ``y``, ``z`` or a ``coords`` sequence
    (as in MoLib ``Atom3D``). The default color function colors by ``chain_id``;
    pass a custom ``color_fn(atom)`` for other schemes.
    """

    draw_mode = GLDrawMode.TRIANGLES

    def __init__(
        self,
        atoms: Sequence[Any],
        *,
        color_fn: Callable[[Any], tuple[float, float, float]] = _default_atom_color,
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
        """Instanciate sphere geometry at each atom and assign per-atom colors."""
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
            color = self.color_fn(atom)
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
