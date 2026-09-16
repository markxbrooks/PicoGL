"""Accumulate position, normal, color, and index mesh arrays."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from picogl.renderer.mesh_arrays import MeshArrays
from picogl.renderer.meshdata import MeshData


class PNCBuffer:
    """Accumulate indexed position / normal / color geometry.

    This class does not construct primitives. Geometry producers append via
    :meth:`extend` (world-space :class:`~picogl.renderer.mesh_arrays.MeshArrays`)
    or :meth:`add_instance` / :meth:`add_instances` (translated templates).
    :meth:`to_mesh_arrays` materializes combined geometry; :meth:`to_mesh_data`
    is the render boundary.
    """

    def __init__(self) -> None:
        self._positions: list[np.ndarray] = []
        self._normals: list[np.ndarray] = []
        self._colors: list[np.ndarray] = []
        self._indices: list[np.ndarray] = []
        self.vertex_offset: int = 0

    def add_instance(
        self,
        mesh: MeshArrays,
        translation: Iterable[float],
        color: tuple[float, float, float],
        *,
        scale: float = 1.0,
    ) -> None:
        """Translate a geometry template and append it with a uniform color.

        Template colors are ignored; *color* is tiled onto every new vertex.

        :param mesh: Origin-centered positions, normals, and local indices
        :param translation: World-space offset applied to every template vertex
        :param color: RGB triple copied onto every new vertex
        :param scale: Uniform scale applied to template positions before translation
        """
        self.add_instances(
            mesh,
            np.asarray(translation, dtype=np.float32).reshape(1, 3),
            np.asarray(color, dtype=np.float32).reshape(1, 3),
            scales=np.asarray([scale], dtype=np.float32),
        )

    def add_instances(
        self,
        mesh: MeshArrays,
        translations: np.ndarray,
        colors: np.ndarray,
        *,
        scales: np.ndarray | None = None,
    ) -> None:
        """Translate one template to many instances in a single NumPy expand.

        Template colors are ignored; each row of *colors* is tiled onto that
        instance's vertices.

        :param mesh: Origin-centered positions, normals, and local indices
        :param translations: World-space offsets with shape ``(N, 3)``
        :param colors: Per-instance RGB triples with shape ``(N, 3)``
        :param scales: Optional per-instance uniform scales with shape ``(N,)``
        """
        translations = np.asarray(translations, dtype=np.float32)
        if translations.ndim != 2:
            translations = translations.reshape(-1, 3)
        n_inst = int(translations.shape[0])
        if n_inst == 0:
            return
        colors = np.asarray(colors, dtype=np.float32)
        if colors.ndim != 2:
            colors = colors.reshape(-1, 3)
        if colors.shape[0] != n_inst:
            raise ValueError("colors must have one RGB triple per translation")
        verts = np.asarray(mesh.positions, dtype=np.float32)
        n_verts = int(verts.shape[0])
        instanced = verts[None, :, :]
        if scales is not None:
            scales_arr = np.asarray(scales, dtype=np.float32).reshape(-1)
            if scales_arr.shape[0] != n_inst:
                raise ValueError("scales must have one value per translation")
            instanced = instanced * scales_arr.reshape(-1, 1, 1)
        out_vertices = (instanced + translations[:, None, :]).reshape(-1, 3)
        out_normals = np.tile(np.asarray(mesh.normals, dtype=np.float32), (n_inst, 1))
        out_colors = np.repeat(colors, n_verts, axis=0)
        if mesh.indices is None:
            out_indices = np.zeros((0,), dtype=np.uint32)
        else:
            local = np.asarray(mesh.indices, dtype=np.uint32).ravel()
            offsets = np.uint32(self.vertex_offset) + np.arange(
                n_inst, dtype=np.uint32
            ) * np.uint32(n_verts)
            out_indices = (local[None, :] + offsets[:, None]).reshape(-1)
        self._append_chunk(
            out_vertices, out_normals, out_colors, out_indices, n_inst * n_verts
        )

    def extend(
        self,
        mesh: MeshArrays,
        *,
        color: tuple[float, float, float] | None = None,
    ) -> None:
        """Append world-space geometry and offset local indices.

        :param mesh: Positions, normals, and indices already in world space
        :param color: Optional RGB triple tiled onto every vertex. Used when
            given; otherwise *mesh.colors* is required.
        :raises ValueError: If neither *color* nor *mesh.colors* is present
        """
        verts = np.asarray(mesh.positions, dtype=np.float32)
        n_verts = int(verts.shape[0])
        norms = np.asarray(mesh.normals, dtype=np.float32)
        cols = self._resolve_colors(mesh, n_verts, color)
        indices = self._offset_indices(mesh.indices)
        self._append_chunk(verts, norms, cols, indices, n_verts)

    def _resolve_colors(
        self,
        mesh: MeshArrays,
        n_verts: int,
        color: tuple[float, float, float] | None,
    ) -> np.ndarray:
        if color is not None:
            rgb = np.asarray(color, dtype=np.float32).reshape(3)
            return np.broadcast_to(rgb, (n_verts, 3)).copy()
        if mesh.colors is None:
            raise ValueError("PNCBuffer.extend requires mesh.colors or color=")
        return np.asarray(mesh.colors, dtype=np.float32)

    def _offset_indices(self, indices: np.ndarray | None) -> np.ndarray:
        if indices is None:
            return np.zeros((0,), dtype=np.uint32)
        idxs = np.asarray(indices, dtype=np.uint32).ravel()
        if idxs.size:
            idxs = idxs + np.uint32(self.vertex_offset)
        return idxs

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

    def to_mesh_arrays(self) -> MeshArrays:
        """Materialize accumulated chunks as combined geometry.

        :return: Positions, normals, colors, and offset triangle indices
        """
        verts, norms, cols, idxs = self.to_arrays()
        return MeshArrays(
            positions=verts,
            normals=norms,
            colors=cols,
            indices=idxs,
        )

    def to_mesh_data(self) -> MeshData:
        """Build renderable :class:`~picogl.renderer.meshdata.MeshData`.

        :return: Mesh with positions, normals, colors, and triangle indices
        """
        return self.to_mesh_arrays().as_meshdata()

    def to_arrays(
        self, dtype: np.dtype | type = np.float32
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return concatenated NumPy arrays for :meth:`to_mesh_arrays`.

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
