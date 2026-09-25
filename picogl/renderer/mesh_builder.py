"""Accumulate indexed mesh parts into a single MeshData."""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np
from picogl.renderer.meshdata import MeshData

# (vertices, faces/indices, normals, colors)
MeshPart = Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]


def solid_color_mesh_part(
    vertices: np.ndarray,
    faces: np.ndarray,
    normals: np.ndarray,
    color: Tuple[float, float, float] = (0.7, 0.7, 0.7),
) -> MeshPart:
    """Build a :data:`MeshPart` with a single RGB colour tiled per vertex.

    :param vertices: ``(N, 3)`` positions
    :param faces: ``(M, 3)`` or flat index buffer
    :param normals: ``(N, 3)`` normals
    :param color: RGB triple in ``[0, 1]``
    :return: MeshPart tuple
    """
    colors = np.tile(np.asarray(color, dtype=np.float32), (len(vertices), 1))
    return vertices, faces, normals, colors


def mesh_part_from_pnc(pnc, faces: np.ndarray) -> MeshPart:
    """Attach face indices to a :data:`~picogl.renderer.meshdata.PNCPart`.

    :param pnc: ``(positions, normals, colors)``
    :param faces: ``(M, 3)`` or flat index buffer
    :return: MeshPart ``(positions, faces, normals, colors)``
    """
    positions, normals, colors = pnc
    return positions, faces, normals, colors


class MeshBuilder:
    """Accumulate mesh parts into one indexed mesh with face-index offsets.

    Each part is ``(vertices, faces, normals, colors)``. Face indices in
    subsequent parts are offset so they remain valid after concatenation.
    """

    def __init__(self) -> None:
        self.vertices: List[np.ndarray] = []
        self.faces: List[np.ndarray] = []
        self.normals: List[np.ndarray] = []
        self.colors: List[np.ndarray] = []
        self.vertex_offset = 0

    def add_part(self, part: Optional[MeshPart]) -> None:
        """Append one mesh part, skipping ``None`` / empty vertex arrays.

        :param part: ``(vertices, faces, normals, colors)`` or ``None``.
            ``faces`` may be ``(M, 3)`` triangles or a flat index buffer.
        """
        if part is None:
            return
        vtx, fcs, nrms, cols = part
        if vtx is None or len(vtx) == 0:
            return
        faces = np.asarray(fcs)
        if faces.ndim not in (1, 2):
            raise ValueError(
                "faces must be 1-D or 2-D, got shape {0}".format(faces.shape)
            )
        if self.faces and np.asarray(self.faces[0]).ndim != faces.ndim:
            raise ValueError(
                "mixed face layouts in one MeshBuilder "
                "(all parts must use flat or (M, K) faces)"
            )
        self.vertices.append(vtx)
        self.faces.append(faces + self.vertex_offset)
        self.normals.append(nrms)
        self.colors.append(cols)
        self.vertex_offset += len(vtx)

    def build(self) -> Optional[MeshPart]:
        """Stack accumulated parts into ``(vertices, faces, normals, colors)``.

        :return: Stacked :data:`MeshPart`, or ``None`` when no parts were added
        """
        if not self.vertices:
            return None
        first_faces = np.asarray(self.faces[0])
        if first_faces.ndim == 1:
            faces = np.concatenate(self.faces).astype(np.uint32, copy=False)
        else:
            faces = np.vstack(self.faces).astype(np.uint32, copy=False)
        return (
            np.vstack(self.vertices).astype(np.float32, copy=False),
            faces,
            np.vstack(self.normals).astype(np.float32, copy=False),
            np.vstack(self.colors).astype(np.float32, copy=False),
        )

    def mesh_data(self) -> Optional[MeshData]:
        """Build a :class:`~picogl.renderer.meshdata.MeshData` from parts.

        :return: MeshData, or ``None`` when no parts were added
        """
        stacked = self.build()
        if stacked is None:
            return None
        vertices, faces, normals, colors = stacked
        return MeshData.from_raw(
            vertices=vertices,
            indices=faces,
            colors=colors,
            normals=normals,
        )

    def __enter__(self) -> "MeshBuilder":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        return False

    def __repr__(self) -> str:
        return (
            "MeshBuilder(parts={0}, vertex_offset={1})".format(
                len(self.vertices),
                self.vertex_offset,
            )
        )


def stack_mesh_parts(
    parts: Sequence[Optional[MeshPart]],
) -> Optional[MeshPart]:
    """Concatenate mesh parts with face-index offsets.

    :param parts: Sequence of mesh parts (``None`` / empty skipped)
    :return: Stacked :data:`MeshPart`, or ``None``
    """
    builder = MeshBuilder()
    for part in parts:
        builder.add_part(part)
    return builder.build()
