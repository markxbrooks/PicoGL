"""Line-segment bond mesh for molecular visualization."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.meshdata import MeshData
from picogl.renderer.molecular.atoms import atom_xyz
from picogl.renderer.molecular.base import MolecularMesh
from picogl.renderer.molecular.colors import chain_rgb
from picogl.renderer.molecular.pnc_buffer import PNCBuffer


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

        buf = PNCBuffer()
        zero_n = (0.0, 0.0, 1.0)
        for atom1, atom2 in self.bonds:
            color = self.color_fn(atom1.chain_id)
            x1, y1, z1 = atom_xyz(atom1)
            x2, y2, z2 = atom_xyz(atom2)
            buf.extend_direct(
                positions=((x1, y1, z1), (x2, y2, z2)),
                normals=(zero_n, zero_n),
                colors=(color, color),
                indices=(0, 1),
            )

        verts, _norms, cols, idxs = buf.to_arrays()
        return MeshData.from_raw(vertices=verts, colors=cols, indices=idxs)
