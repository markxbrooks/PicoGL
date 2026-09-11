"""Sphere-instanced atom mesh for molecular visualization."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np

from molib.calc.math.vector import Vector3
from molib.entities.atom import Atom3D
from molib.pdb.color import palette_rgb_at
from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.draw_spec import MeshDrawInfo
from picogl.renderer.meshdata import MeshData
from picogl.renderer.molecular.atom_geometry import AtomGeometry
from picogl.renderer.molecular.base import MolecularMesh
from picogl.renderer.molecular.pnc_buffer import PNCBuffer

from collections.abc import Callable, Sequence
from typing import Any

def make_chain_color_fn(
    chain_ids: Sequence[str],
    ) -> Callable[[Any], tuple[float, float, float]]:
    """
    Create a per-atom color function that assigns colors by chain ID.

    ```
    Chain IDs are sorted and deduplicated so that the resulting colors are
    deterministic and match :func:`generate_chain_colors` when ``chain_ids``
    contains every chain in the structure.
    """
    unique_sorted = sorted(set(chain_ids))

    # Precompute the mapping once rather than sorting/indexing for every atom.
    color_map = {
        chain_id: palette_rgb_at(index)
        for index, chain_id in enumerate(unique_sorted)
    }

    def color_fn(atom: Any) -> tuple[float, float, float]:
        """Return the palette color corresponding to ``atom.chain_id``."""
        chain_id = atom.chain_id

        if chain_id not in color_map:
            # Preserve the behavior of the original function for an
            # unexpected/missing chain ID.
            color_map[chain_id] = palette_rgb_at(len(color_map))

        return color_map[chain_id]

    return color_fn


def atom_xyz(atom: Atom3D | Vector3 | np.ndarray) -> tuple[float, float, float]:
    """Return ``(x, y, z)`` from ``atom.x/y/z`` (e.g. Vector3 object) or ``atom.coords`` (e.g. Atom3D)."""
    coords = getattr(atom, "coords", None)
    if coords is not None:
        return float(coords[0]), float(coords[1]), float(coords[2])
    return float(atom.x), float(atom.y), float(atom.z)


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
        color_fn: Callable[[Any], tuple[float, float, float]] = None,
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

        mesh_data = buf.to_mesh_data()
        mesh_data.draw_info = MeshDrawInfo(
            mode=GLDrawMode.TRIANGLES,
            indexed=True,
            elements_per_item=self.geometry.elements_per_item,
            vertices_per_item=self.geometry.vertices_per_item,
        )
        return mesh_data
