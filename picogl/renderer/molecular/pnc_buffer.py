"""Accumulate position, normal, color, and index mesh arrays."""

from __future__ import annotations

from collections.abc import Iterable
from typing import List, Tuple

import numpy as np

from picogl.renderer.meshdata import MeshData


class PNCBuffer:
    """Accumulate indexed position / normal / color geometry.

    This class does not construct primitives. Geometry producers append via
    :meth:`extend` or :meth:`add_instance`; :meth:`to_arrays` materializes
    NumPy buffers for :meth:`MeshData.from_raw`.
    """

    def __init__(self) -> None:
        self.positions: List[List[float]] = []
        self.normals: List[List[float]] = []
        self.colors: List[Tuple[float, float, float]] = []
        self.indices: List[int] = []
        self.vertex_offset: int = 0

    def add_instance(
        self,
        translation: Iterable[float],
        template_vertices: Iterable[Iterable[float]],
        template_normals: Iterable[Iterable[float]],
        template_indices: Iterable[int],
        color: Tuple[float, float, float],
    ) -> None:
        """Translate a geometry template and append it with a uniform color.

        Parameters
        ----------
        translation
            World-space offset applied to every template vertex.
        template_vertices
            Template positions, typically ``(N, 3)``.
        template_normals
            Template normals, same length as ``template_vertices``.
        template_indices
            Triangle indices relative to the template.
        color
            RGB triple copied onto every new vertex.
        """
        tx, ty, tz = (float(c) for c in translation)
        vertices = list(template_vertices)
        for vertex in vertices:
            self.positions.append(
                [float(vertex[0]) + tx, float(vertex[1]) + ty, float(vertex[2]) + tz]
            )
            self.colors.append(color)
        for normal in template_normals:
            self.normals.append([float(normal[0]), float(normal[1]), float(normal[2])])
        for idx in template_indices:
            self.indices.append(int(idx) + self.vertex_offset)
        self.vertex_offset += len(vertices)

    def extend(
        self,
        positions: Iterable[Iterable[float]],
        normals: Iterable[Iterable[float]],
        colors: Iterable[Tuple[float, float, float]],
        indices: Iterable[int],
    ) -> None:
        """Append world-space vertex attributes and offset local indices.

        Parameters
        ----------
        positions
            Vertex positions already in world space.
        normals
            Per-vertex normals.
        colors
            Per-vertex RGB triples.
        indices
            Triangle indices relative to this batch (not the whole buffer).
        """
        vertices = list(positions)
        for position in vertices:
            self.positions.append(
                [float(position[0]), float(position[1]), float(position[2])]
            )
        for normal in normals:
            self.normals.append([float(normal[0]), float(normal[1]), float(normal[2])])
        for color in colors:
            self.colors.append((float(color[0]), float(color[1]), float(color[2])))
        for idx in indices:
            self.indices.append(int(idx) + self.vertex_offset)
        self.vertex_offset += len(vertices)

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

        Parameters
        ----------
        dtype
            Floating-point dtype for positions, normals, and colors.

        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
            ``(vertices, normals, colors, indices)``.
        """
        vertices = (
            np.array(self.positions, dtype=dtype)
            if self.positions
            else np.zeros((0, 3), dtype=dtype)
        )
        normals = (
            np.array(self.normals, dtype=dtype)
            if self.normals
            else np.zeros((0, 3), dtype=dtype)
        )
        colors = (
            np.array(self.colors, dtype=dtype)
            if self.colors
            else np.zeros((0, 3), dtype=dtype)
        )
        indices = (
            np.array(self.indices, dtype=np.uint32)
            if self.indices
            else np.zeros((0,), dtype=np.uint32)
        )
        return vertices, normals, colors, indices
