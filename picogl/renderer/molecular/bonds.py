"""Line-segment bond mesh for molecular visualization."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np

from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.meshdata import MeshData
from picogl.renderer.molecular.base import MolecularMesh
from picogl.renderer.molecular.colors import chain_rgb


def add_bond_to_vertices(atom1, atom2, vertices: list[list[float]]):
    """add bond to vertices"""
    add_atom_vertex_to_vertices(atom1, vertices)
    add_atom_vertex_to_vertices(atom2, vertices)


def add_atom_vertex_to_vertices(atom, vertices: list[list[float]]):
    """add atom to vertices"""
    vertices.append([atom.x, atom.y, atom.z])


class BondsMesh(MolecularMesh):
    """
    Build line meshes connecting pairs of atoms.

    Each bond is a pair ``(atom1, atom2)`` with ``x``, ``y``, ``z``, and
    ``chain_id`` on each atom. Color is taken from the first atom's chain.
    """

    draw_mode = GLDrawMode.LINES

    def __init__(
        self,
        bonds: Sequence[tuple[Any, Any]],
        *,
        color_fn: Callable[[str], tuple[float, float, float]] = chain_rgb,
    ) -> None:
        super().__init__()
        self.bonds = bonds
        self.color_fn = color_fn

    def build_mesh_data(self) -> MeshData:
        """Build two-vertex line segments for each bond."""
        if not self.bonds:
            return MeshData.from_raw(
                vertices=np.zeros((0, 3), dtype=np.float32),
                indices=np.zeros((0,), dtype=np.uint32),
            )

        vertices: list[list[float]] = []
        colors: list[tuple[float, float, float]] = []
        indices: list[int] = []

        for atom1, atom2 in self.bonds:
            color = self.color_fn(atom1.chain_id)
            start_idx = len(vertices)
            add_bond_to_vertices(atom1, atom2, vertices)
            colors.extend([color, color])
            indices.extend([start_idx, start_idx + 1])

        return MeshData.from_raw(
            vertices=np.array(vertices, dtype=np.float32),
            colors=np.array(colors, dtype=np.float32),
            indices=np.array(indices, dtype=np.uint32),
        )
