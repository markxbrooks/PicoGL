"""Sphere-instanced atom mesh for molecular visualization."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np

from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.draw_spec import MeshDrawInfo
from picogl.renderer.meshdata import MeshData
from picogl.renderer.molecular.atom_geometry import AtomGeometry
from picogl.renderer.molecular.base import MolecularMesh
from picogl.renderer.molecular.colors import chain_rgb
from picogl.renderer.molecular.pnc_buffer import PNCBuffer


def atom_xyz(atom: Any) -> tuple[float, float, float]:
    """Return ``(x, y, z)`` from ``atom.x/y/z`` or ``atom.coords`` (e.g. Atom3D)."""
    coords = getattr(atom, "coords", None)
    if coords is not None:
        return float(coords[0]), float(coords[1]), float(coords[2])
    return float(atom.x), float(atom.y), float(atom.z)


def _default_atom_color(atom: Any) -> tuple[float, float, float]:
    """Default color from atom ``chain_id`` (compatible with :func:`chain_rgb`)."""
    return chain_rgb(getattr(atom, "chain_id", ""))


class AtomsMesh(MolecularMesh):
    """
    Build triangle meshes by instancing a sphere template at each atom position.

    Atoms must expose either ``x``, ``y``, ``z`` or a ``coords`` sequence
    (as in MoLib ``Atom3D``). The default color function colors by ``chain_id``;
    pass a custom ``color_fn(atom)`` for other schemes.

    ``radius``, ``slices``, and ``stacks`` construct an :class:`AtomGeometry`
    when ``geometry`` is omitted.
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
        geometry: AtomGeometry | None = None,
    ) -> None:
        super().__init__()
        self.atoms = atoms
        self.color_fn = color_fn
        self.geometry = geometry or AtomGeometry(
            radius=radius, slices=slices, stacks=stacks
        )

    @property
    def radius(self) -> float:
        """Sphere radius from :attr:`geometry`."""
        return self.geometry.radius

    @property
    def slices(self) -> int:
        """Longitudinal subdivisions from :attr:`geometry`."""
        return self.geometry.slices

    @property
    def stacks(self) -> int:
        """Latitudinal subdivisions from :attr:`geometry`."""
        return self.geometry.stacks

    def build_mesh_data(self) -> MeshData:
        """Instance sphere geometry at each atom and assign per-atom colors."""
        if not self.atoms:
            return self._empty_mesh_data(
                elements_per_item=self.geometry.elements_per_item,
                vertices_per_item=self.geometry.vertices_per_item,
            )

        template = self.geometry.build()
        template_vertices = np.asarray(template.vertices, dtype=np.float32).reshape(
            -1, 3
        )
        template_normals = np.asarray(template.normals, dtype=np.float32).reshape(-1, 3)
        template_indices = np.asarray(template.indices, dtype=np.uint32).ravel()

        buf = PNCBuffer()
        for atom in self.atoms:
            buf.add_instance(
                atom_xyz(atom),
                template_vertices,
                template_normals,
                template_indices,
                self.color_fn(atom),
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
