"""Oriented cylinder geometry for a single bond."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from picogl.renderer.meshdata import MeshData

_MIN_BOND_LENGTH = 1e-12


@dataclass(frozen=True, slots=True)
class BondGeometry:
    """Geometry parameters for a cylindrical bond shaft.

    Builds an open-sided cylinder between two world-space points. Color is
    applied by :class:`~picogl.renderer.molecular.bonds.BondsMesh`.
    """

    radius: float = 0.06
    segments: int = 8

    def build(self, start: Iterable[float], end: Iterable[float]) -> MeshData:
        """Build an oriented cylinder spanning ``start`` to ``end``.

        Parameters
        ----------
        start
            World-space cylinder origin.
        end
            World-space cylinder terminus.

        Returns
        -------
        MeshData
            Positions, radial normals, and indices. Empty when the axis
            length is below ``1e-12``.
        """
        positions, normals, indices = self._cylinder(start, end)
        return MeshData.from_raw(
            vertices=positions,
            normals=normals,
            indices=indices,
        )

    @property
    def vertices_per_item(self) -> int:
        """Number of vertices in one cylinder (two rings)."""
        return 2 * self.segments

    @property
    def elements_per_item(self) -> int:
        """Number of triangle indices in one cylinder."""
        return 6 * self.segments

    def _cylinder(
        self,
        start: Iterable[float],
        end: Iterable[float],
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return ``(positions, normals, indices)`` for the shaft."""
        empty = (
            np.zeros((0, 3), dtype=np.float32),
            np.zeros((0, 3), dtype=np.float32),
            np.zeros((0,), dtype=np.uint32),
        )
        origin = np.asarray(start, dtype=np.float64)
        terminus = np.asarray(end, dtype=np.float64)
        axis = terminus - origin
        length = float(np.linalg.norm(axis))
        if length < _MIN_BOND_LENGTH:
            return empty

        direction = axis / length
        reference = np.array([0.0, 0.0, 1.0])
        if abs(float(np.dot(direction, reference))) > 0.99:
            reference = np.array([1.0, 0.0, 0.0])
        basis_u = np.cross(direction, reference)
        basis_u /= np.linalg.norm(basis_u)
        basis_v = np.cross(direction, basis_u)

        positions: list[list[float]] = []
        normals: list[list[float]] = []
        for k in range(self.segments):
            angle = 2.0 * np.pi * k / self.segments
            radial = basis_u * math.cos(angle) + basis_v * math.sin(angle)
            positions.append((origin + radial * self.radius).tolist())
            positions.append((terminus + radial * self.radius).tolist())
            normals.append(radial.tolist())
            normals.append(radial.tolist())

        indices: list[int] = []
        for k in range(self.segments):
            k1 = (k + 1) % self.segments
            bottom_current, top_current = 2 * k, 2 * k + 1
            bottom_next, top_next = 2 * k1, 2 * k1 + 1
            indices.extend(
                (
                    bottom_current,
                    bottom_next,
                    top_current,
                    bottom_next,
                    top_next,
                    top_current,
                )
            )

        return (
            np.asarray(positions, dtype=np.float32),
            np.asarray(normals, dtype=np.float32),
            np.asarray(indices, dtype=np.uint32),
        )
