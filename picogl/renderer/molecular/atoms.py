"""Sphere-instanced atom mesh for molecular visualization."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np

from picogl.backend.gl.enums import GLDrawMode
from picogl.core.geometry.sphere import unit_sphere_mesh
from picogl.renderer.draw_spec import MeshDrawInfo
from picogl.renderer.meshdata import MeshData
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
        """Instance sphere geometry at each atom and assign per-atom colors."""
        if not self.atoms:
            template_vertices, _, template_indices = unit_sphere_mesh(
                self.radius, self.slices, self.stacks
            )
            data = MeshData.from_raw(
                vertices=np.zeros((0, 3), dtype=np.float32),
                indices=np.zeros((0,), dtype=np.uint32),
            )
            data.draw_info = MeshDrawInfo(
                mode=GLDrawMode.TRIANGLES,
                indexed=True,
                elements_per_item=int(template_indices.size),
                vertices_per_item=int(template_vertices.shape[0]),
            )
            return data

        template_vertices, template_normals, template_indices = unit_sphere_mesh(
            self.radius, self.slices, self.stacks
        )
        # Materialize once so each add_instance can re-iterate the template.
        template_vertices = list(template_vertices)
        template_normals = list(template_normals)
        template_indices = list(template_indices)

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
        n_template_verts = len(template_vertices)
        n_template_idx = len(template_indices)
        data.draw_info = MeshDrawInfo(
            mode=GLDrawMode.TRIANGLES,
            indexed=True,
            elements_per_item=n_template_idx,
            vertices_per_item=n_template_verts,
        )
        return data
