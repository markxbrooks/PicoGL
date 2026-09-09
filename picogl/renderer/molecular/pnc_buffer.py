"""Builder for interleaved position / normal / color / index mesh arrays."""

from __future__ import annotations

import math
from collections.abc import Iterable
from typing import List, Tuple

import numpy as np


class PNCBuffer:
    """Hold and build arrays of positions, normals, colors and indices.

    Usage::

        buf = PNCBuffer()
        buf.add_instance(
            translation, template_vertices, template_normals, template_indices, color
        )
        vertices, normals, colors, indices = buf.to_arrays()
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
        """Translate template vertices, copy normals/colors, offset indices."""
        tx, ty, tz = (float(c) for c in translation)
        n_new = 0
        for vertex in template_vertices:
            self.positions.append(
                [float(vertex[0]) + tx, float(vertex[1]) + ty, float(vertex[2]) + tz]
            )
            self.colors.append(color)
            n_new += 1
        for normal in template_normals:
            self.normals.append(
                [float(normal[0]), float(normal[1]), float(normal[2])]
            )
        for idx in template_indices:
            self.indices.append(int(idx) + self.vertex_offset)
        self.vertex_offset += n_new

    def extend_direct(
        self,
        positions: Iterable[Iterable[float]],
        normals: Iterable[Iterable[float]],
        colors: Iterable[Tuple[float, float, float]],
        indices: Iterable[int],
    ) -> None:
        """Append already-world-space vertex attributes (indices relative to this batch)."""
        n_new = 0
        for position in positions:
            self.positions.append(
                [float(position[0]), float(position[1]), float(position[2])]
            )
            n_new += 1
        for normal in normals:
            self.normals.append([float(normal[0]), float(normal[1]), float(normal[2])])
        for color in colors:
            self.colors.append((float(color[0]), float(color[1]), float(color[2])))
        for idx in indices:
            self.indices.append(int(idx) + self.vertex_offset)
        self.vertex_offset += n_new

    def add_cylinder(
        self,
        start: Iterable[float],
        end: Iterable[float],
        color: Tuple[float, float, float],
        radius: float = 0.1,
        segments: int = 8,
    ) -> None:
        """Append an open-sided cylinder spanning ``start`` to ``end``.

        Generates ``2 * segments`` vertices (two rings around the axis) with
        outward radial normals, so the shaft lights correctly regardless of
        bond orientation. The cylinder is open at both ends.
        """
        s = np.asarray(start, dtype=np.float64)
        e = np.asarray(end, dtype=np.float64)
        axis = e - s
        length = float(np.linalg.norm(axis))
        if length < 1e-12:
            return
        direction = axis / length

        reference = np.array([0.0, 0.0, 1.0])
        if abs(float(np.dot(direction, reference))) > 0.99:
            reference = np.array([1.0, 0.0, 0.0])
        basis_u = np.cross(direction, reference)
        basis_u /= np.linalg.norm(basis_u)
        basis_v = np.cross(direction, basis_u)

        positions: List[List[float]] = []
        normals: List[List[float]] = []
        for k in range(segments):
            angle = 2.0 * np.pi * k / segments
            radial = basis_u * math.cos(angle) + basis_v * math.sin(angle)
            positions.append((s + radial * radius).tolist())
            positions.append((e + radial * radius).tolist())
            normals.append(radial.tolist())
            normals.append(radial.tolist())

        colors = [tuple(float(c) for c in color)] * len(positions)
        indices: List[int] = []
        for k in range(segments):
            k1 = (k + 1) % segments
            bottom_current, top_current = 2 * k, 2 * k + 1
            bottom_next, top_next = 2 * k1, 2 * k1 + 1
            indices.append(bottom_current)
            indices.append(bottom_next)
            indices.append(top_current)
            indices.append(bottom_next)
            indices.append(top_next)
            indices.append(top_current)

        self.extend_direct(
            positions=positions,
            normals=normals,
            colors=colors,
            indices=indices,
        )

    def to_arrays(
        self, dtype: np.dtype | type = np.float32
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return numpy arrays suitable for :meth:`MeshData.from_raw`."""
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
