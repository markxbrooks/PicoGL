"""Accumulate position, normal, color, and index mesh arrays."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Tuple

import numpy as np

from picogl.renderer.mesh_arrays import MeshArrays
from picogl.renderer.meshdata import MeshData


class PNCBuffer:
    """Accumulate indexed position / normal / color geometry.

    This class does not construct primitives. Geometry producers append via
    :meth:`extend` or :meth:`add_instance`; :meth:`to_arrays` materializes
    NumPy buffers for :meth:`MeshData.from_raw`.
    """

    def __init__(self) -> None:
        self._positions: list[np.ndarray] = []
        self._normals: list[np.ndarray] = []
        self._colors: list[np.ndarray] = []
        self._indices: list[np.ndarray] = []
        self.vertex_offset: int = 0

    def add_instance(
        self,
        translation: Iterable[float],
        template: MeshArrays,
        color: Tuple[float, float, float],
        *,
        scale: float = 1.0,
    ) -> None:
        """Translate a geometry template and append it with a uniform color.

        :param translation: World-space offset applied to every template vertex
        :param template: Origin-centered positions, normals, and local indices
        :param color: RGB triple copied onto every new vertex
        :param scale: Uniform scale applied to template positions before translation
        """
        verts = np.asarray(template.positions, dtype=np.float32)
        if scale != 1.0:
            verts = verts * np.float32(scale)
        verts = verts + np.asarray(translation, dtype=np.float32).reshape(1, 3)
        n_verts = int(verts.shape[0])
        rgb = np.asarray(color, dtype=np.float32).reshape(3)
        colors = np.broadcast_to(rgb, (n_verts, 3)).copy()
        normals = np.asarray(template.normals, dtype=np.float32)
        if template.indices is None:
            indices = np.zeros((0,), dtype=np.uint32)
        else:
            indices = np.asarray(template.indices, dtype=np.uint32).ravel()
            indices = indices + np.uint32(self.vertex_offset)
        self._append_chunk(verts, normals, colors, indices, n_verts)

    def extend(
        self,
        positions: Iterable[Iterable[float]],
        normals: Iterable[Iterable[float]],
        colors: Iterable[Tuple[float, float, float]],
        indices: Iterable[int],
    ) -> None:
        """Append world-space vertex attributes and offset local indices.

        :param positions: Vertex positions already in world space
        :param normals: Per-vertex normals
        :param colors: Per-vertex RGB triples
        :param indices: Triangle indices relative to this batch (not the whole buffer)
        """
        verts = np.asarray(positions, dtype=np.float32)
        if verts.ndim != 2:
            verts = verts.reshape(-1, 3)
        n_verts = int(verts.shape[0])
        norms = np.asarray(normals, dtype=np.float32)
        if norms.ndim != 2:
            norms = norms.reshape(-1, 3)
        cols = np.asarray(colors, dtype=np.float32)
        if cols.ndim != 2:
            cols = cols.reshape(-1, 3)
        idxs = np.asarray(indices, dtype=np.uint32).ravel()
        if idxs.size:
            idxs = idxs + np.uint32(self.vertex_offset)
        self._append_chunk(verts, norms, cols, idxs, n_verts)

    def _append_chunk(
        self,
        positions: np.ndarray,
        normals: np.ndarray,
        colors: np.ndarray,
        indices: np.ndarray,
        n_verts: int,
    ) -> None:
        self._positions.append(positions)
        self._normals.append(normals)
        self._colors.append(colors)
        self._indices.append(indices)
        self.vertex_offset += n_verts

    def to_mesh_data(self) -> MeshData:
        """Build a :class:`~picogl.renderer.meshdata.MeshData` from accumulated arrays.

        :return: Mesh with positions, normals, colors, and triangle indices
        """
        verts, norms, cols, idxs = self.to_arrays()
        return MeshData.from_raw(
            vertices=verts, normals=norms, colors=cols, indices=idxs
        )

    def to_arrays(
        self, dtype: np.dtype | type = np.float32
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return NumPy arrays suitable for :meth:`MeshData.from_raw`.

        :param dtype: Floating-point dtype for positions, normals, and colors
        :return: ``(vertices, normals, colors, indices)``
        """
        if not self._positions:
            return (
                np.zeros((0, 3), dtype=dtype),
                np.zeros((0, 3), dtype=dtype),
                np.zeros((0, 3), dtype=dtype),
                np.zeros((0,), dtype=np.uint32),
            )
        vertices = np.concatenate(self._positions, axis=0).astype(dtype, copy=False)
        normals = np.concatenate(self._normals, axis=0).astype(dtype, copy=False)
        colors = np.concatenate(self._colors, axis=0).astype(dtype, copy=False)
        if any(chunk.size for chunk in self._indices):
            indices = np.concatenate(self._indices, axis=0)
        else:
            indices = np.zeros((0,), dtype=np.uint32)
        return vertices, normals, colors, indices
