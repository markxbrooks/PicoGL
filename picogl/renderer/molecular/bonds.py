"""Cylinder bond mesh for molecular visualization."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.meshdata import MeshData
from picogl.renderer.molecular.atoms import atom_xyz
from picogl.renderer.molecular.atoms import _default_atom_color
from picogl.renderer.molecular.base import MolecularMesh
from picogl.renderer.molecular.pnc_buffer import PNCBuffer


class BondsMesh(MolecularMesh):
    """
    Build cylinder meshes connecting pairs of atoms.

    Each bond is a pair ``(atom1, atom2)`` with ``x``, ``y``, ``z``, and
    ``chain_id`` on each atom. Color is taken from the first atom, mirroring
    :class:`picogl.renderer.molecular.atoms.AtomsMesh` semantics.
    """

    draw_mode = GLDrawMode.TRIANGLES

    def __init__(
        self,
        bonds: Sequence[tuple["Atom3D", "Atom3D"]],
        *,
        color_fn: Callable[[Any], tuple[float, float, float]] = _default_atom_color,
        radius: float = 0.06,
        segments: int = 8,
    ) -> None:
        super().__init__()
        self.bonds = bonds
        self.color_fn = color_fn
        self.radius = radius
        self.segments = segments

    def build_mesh_data(self) -> MeshData:
        """Build an oriented cylinder shaft for each bond."""
        if not self.bonds:
            return MeshData.from_raw(
                vertices=np.zeros((0, 3), dtype=np.float32),
                indices=np.zeros((0,), dtype=np.uint32),
            )

        buf = PNCBuffer()
        for atom1, atom2 in self.bonds:
            buf.add_cylinder(
                start=atom_xyz(atom1),
                end=atom_xyz(atom2),
                color=self.color_fn(atom1),
                radius=self.radius,
                segments=self.segments,
            )

        verts, _norms, cols, idxs = buf.to_arrays()
        return MeshData.from_raw(vertices=verts, colors=cols, indices=idxs)
