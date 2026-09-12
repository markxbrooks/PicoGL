"""Oriented cylinder geometry for a single bond."""

from __future__ import annotations

import functools
from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from picogl.renderer.meshdata import MeshData

_MIN_BOND_LENGTH = 1e-12

_EMPTY_POSITIONS = np.empty((0, 3), dtype=np.float32)
_EMPTY_NORMALS = np.empty((0, 3), dtype=np.float32)
_EMPTY_INDICES = np.empty((0,), dtype=np.uint32)


@functools.lru_cache(maxsize=32)
def _cylinder_ring(segments: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return cached unit-circle ``(cos, sin, local_indices)`` for *segments*."""
    angles = 2.0 * np.pi * np.arange(segments) / segments
    cosines = np.cos(angles)
    sines = np.sin(angles)
    k = np.arange(segments, dtype=np.uint32)
    k1 = (k + 1) % np.uint32(segments)
    local_indices = np.stack(
        (
            2 * k,
            2 * k1,
            2 * k + 1,
            2 * k1,
            2 * k1 + 1,
            2 * k + 1,
        ),
        axis=1,
    ).reshape(-1)
    return cosines, sines, local_indices


@dataclass(frozen=True, slots=True)
class BondGeometry:
    """Geometry parameters for a cylindrical bond shaft.

    Builds an open-sided cylinder between two world-space points. Color is
    applied by :class:`~picogl.renderer.molecular.bonds.BondsMesh`.
    """

    radius: float = 0.06
    segments: int = 8

    @property
    def vertices_per_item(self) -> int:
        """Number of vertices in one cylinder (two rings)."""
        return 2 * self.segments

    @property
    def elements_per_item(self) -> int:
        """Number of triangle indices in one cylinder."""
        return 6 * self.segments

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
        positions, normals, indices, _valid = self.build_many(
            np.asarray(start, dtype=np.float64).reshape(1, 3),
            np.asarray(end, dtype=np.float64).reshape(1, 3),
        )
        return MeshData.from_raw(
            vertices=positions,
            normals=normals,
            indices=indices,
        )

    def build_many(
        self,
        starts: np.ndarray,
        ends: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Build cylinders for many bonds simultaneously.

        Zero-length shafts (axis shorter than ``1e-12``) are omitted from the
        returned arrays. The boolean *valid* mask has one entry per input row.

        :param starts: ``(N, 3)`` world-space origins
        :param ends: ``(N, 3)`` world-space termini
        :return: ``(positions, normals, indices, valid)``
        """
        starts_a = np.asarray(starts, dtype=np.float64).reshape(-1, 3)
        ends_a = np.asarray(ends, dtype=np.float64).reshape(-1, 3)
        n_in = int(starts_a.shape[0])
        if n_in == 0:
            return (
                _EMPTY_POSITIONS,
                _EMPTY_NORMALS,
                _EMPTY_INDICES,
                np.zeros((0,), dtype=bool),
            )

        axis = ends_a - starts_a
        lengths = np.linalg.norm(axis, axis=1)
        valid = lengths >= _MIN_BOND_LENGTH
        if not np.any(valid):
            return (
                _EMPTY_POSITIONS,
                _EMPTY_NORMALS,
                _EMPTY_INDICES,
                valid,
            )

        starts_a = starts_a[valid]
        ends_a = ends_a[valid]
        axis = axis[valid]
        lengths = lengths[valid]
        directions = axis / lengths[:, None]

        parallel_z = np.abs(directions[:, 2]) > 0.99
        references = np.where(
            parallel_z[:, None],
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
        )

        basis_u = np.cross(directions, references)
        basis_u /= np.linalg.norm(basis_u, axis=1, keepdims=True)
        basis_v = np.cross(directions, basis_u)

        cosines, sines, local_indices = _cylinder_ring(int(self.segments))
        radial = (
            basis_u[:, None, :] * cosines[None, :, None]
            + basis_v[:, None, :] * sines[None, :, None]
        )
        bottom = starts_a[:, None, :] + radial * self.radius
        top = ends_a[:, None, :] + radial * self.radius
        positions = np.stack((bottom, top), axis=2).reshape(-1, 3)
        normals = np.repeat(radial[:, :, None, :], 2, axis=2).reshape(-1, 3)

        n_kept = int(starts_a.shape[0])
        vertex_offsets = (
            np.arange(n_kept, dtype=np.uint32) * np.uint32(self.vertices_per_item)
        )
        indices = (local_indices[None, :] + vertex_offsets[:, None]).reshape(-1)

        return (
            positions.astype(np.float32, copy=False),
            normals.astype(np.float32, copy=False),
            np.asarray(indices, dtype=np.uint32),
            valid,
        )
