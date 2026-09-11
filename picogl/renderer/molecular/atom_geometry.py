"""Sphere template geometry for a single atom."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from picogl.core.geometry.sphere import unit_sphere_mesh
from picogl.renderer.meshdata import MeshData


@dataclass(frozen=True, slots=True)
class AtomGeometry:
    """Geometry parameters for one atom sphere.

    Builds a reusable unit-sphere template. Instancing across atoms is the
    responsibility of :class:`~picogl.renderer.molecular.atoms.AtomsMesh`.
    """

    radius: float = 0.2
    slices: int = 16
    stacks: int = 16

    def build(self) -> MeshData:
        """Build a sphere template centered at the origin.

        Returns
        -------
        MeshData
            Vertices, normals, and indices with no per-atom colors.
        """
        vertices, normals, indices = self._sphere()
        return MeshData.from_raw(
            vertices=vertices,
            normals=normals,
            indices=indices,
        )

    @property
    def vertices_per_item(self) -> int:
        """Number of vertices in one sphere instance."""
        return (self.stacks + 1) * (self.slices + 1)

    @property
    def elements_per_item(self) -> int:
        """Number of triangle indices in one sphere instance."""
        return 6 * self.stacks * self.slices

    def _sphere(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return ``(vertices, normals, indices)`` for this tessellation."""
        return unit_sphere_mesh(
            radius=self.radius,
            slices=self.slices,
            stacks=self.stacks,
        )
