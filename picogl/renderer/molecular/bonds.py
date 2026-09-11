"""Cylinder bond mesh for molecular visualization."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np

from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.draw_spec import MeshDrawInfo
from picogl.renderer.meshdata import MeshData
from picogl.renderer.molecular.atoms import _default_atom_color, atom_xyz
from picogl.renderer.molecular.base import MolecularMesh
from picogl.renderer.molecular.bond_geometry import BondGeometry
from picogl.renderer.molecular.pnc_buffer import PNCBuffer


class BondsMesh(MolecularMesh):
    """
    Build cylinder meshes connecting pairs of atoms.

    Each bond is a pair ``(atom1, atom2)`` with ``x``, ``y``, ``z``, and
    ``chain_id`` on each atom. Color is taken from the first atom, mirroring
    :class:`~picogl.renderer.molecular.atoms.AtomsMesh` semantics.

    ``radius`` and ``segments`` construct a :class:`BondGeometry` when
    ``geometry`` is omitted.
    """

    draw_mode = GLDrawMode.TRIANGLES

    def __init__(
        self,
        bonds: Sequence[tuple["Atom3D", "Atom3D"]],
        *,
        color_fn: Callable[[Any], tuple[float, float, float]] = _default_atom_color,
        radius: float = 0.06,
        segments: int = 8,
        geometry: BondGeometry | None = None,
    ) -> None:
        super().__init__()
        self.bonds = bonds
        self.color_fn = color_fn
        self.geometry = geometry or BondGeometry(radius=radius, segments=segments)

    @property
    def radius(self) -> float:
        """Cylinder radius from :attr:`geometry`."""
        return self.geometry.radius

    @property
    def segments(self) -> int:
        """Radial segment count from :attr:`geometry`."""
        return self.geometry.segments

    def build_mesh_data(self) -> MeshData:
        """Build an oriented cylinder shaft for each bond."""
        if not self.bonds:
            return self._empty_mesh_data(
                elements_per_item=self.geometry.elements_per_item,
                vertices_per_item=self.geometry.vertices_per_item,
            )

        buf = PNCBuffer()
        for atom1, atom2 in self.bonds:
            piece = self.geometry.build(atom_xyz(atom1), atom_xyz(atom2))
            positions = np.asarray(piece.vertices, dtype=np.float32).reshape(-1, 3)
            if positions.shape[0] == 0:
                continue
            normals = np.asarray(piece.normals, dtype=np.float32).reshape(-1, 3)
            indices = np.asarray(piece.indices, dtype=np.uint32).ravel()
            color = self.color_fn(atom1)
            colors = np.repeat(
                np.asarray(color, dtype=np.float32)[None, :],
                len(positions),
                axis=0,
            )
            buf.extend(
                positions=positions,
                normals=normals,
                colors=colors,
                indices=indices,
            )

        verts, norms, cols, idxs = buf.to_arrays()
        data = MeshData.from_raw(
            vertices=verts, normals=norms, colors=cols, indices=idxs
        )
        data.draw_info = MeshDrawInfo(
            mode=GLDrawMode.TRIANGLES,
            indexed=True,
            elements_per_item=self.geometry.elements_per_item,
            vertices_per_item=self.geometry.vertices_per_item,
        )
        return data
