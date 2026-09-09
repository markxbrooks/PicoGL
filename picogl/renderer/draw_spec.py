"""CPU-side draw layout and draw specifications for :class:`MeshData`.

These types describe *what portion of a mesh to draw*. They contain no OpenGL
objects. A VAO/VBG consumes a :class:`MeshDrawSpec` to issue ``glDraw*``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from picogl.backend.gl.enums import GLDrawMode

_UINT32_BYTES = int(np.dtype(np.uint32).itemsize)


@dataclass(frozen=True)
class MeshDrawInfo:
    """Persistent topology for a mesh (how items map onto vertices/indices).

    :param mode: Primitive mode (``POINTS``, ``LINES``, ``TRIANGLES``, …).
    :param indexed: Whether drawing uses an element buffer.
    :param elements_per_item: Indices per logical item (atom, bond, …), or
        ``None`` when the mesh is not instanced.
    :param vertices_per_item: Vertices per logical item, used when expanding
        per-item attributes such as colors.
    """

    mode: GLDrawMode = GLDrawMode.TRIANGLES
    indexed: bool = False
    elements_per_item: int | None = None
    vertices_per_item: int | None = None


@dataclass(frozen=True)
class MeshDrawSpec:
    """One GL-free draw: mode, element/vertex count, and EBO byte offset.

    :param mode: Primitive mode for ``glDrawArrays`` / ``glDrawElements``.
    :param count: Vertex count (non-indexed) or index count (indexed).
    :param first: First vertex for non-indexed draws.
    :param indexed: Whether ``count`` refers to indices.
    :param pointer: Byte offset into the element buffer for indexed draws.
    """

    mode: GLDrawMode
    count: int
    first: int = 0
    indexed: bool = False
    pointer: int = 0


def infer_draw_info(
    *,
    has_indices: bool,
    index_count: int = 0,
) -> MeshDrawInfo:
    """Infer a conservative layout when the mesh has no explicit ``draw_info``.

    Indexed meshes default to triangles; otherwise points. Line-stick bond
    meshes must set :class:`MeshDrawInfo` explicitly (``LINES``).
    """
    indexed = bool(has_indices and index_count > 0)
    mode = GLDrawMode.TRIANGLES if indexed else GLDrawMode.POINTS
    return MeshDrawInfo(mode=mode, indexed=indexed)


def compute_draw_spec(
    info: MeshDrawInfo,
    *,
    index_count: int = 0,
    vertex_count: int = 0,
    first_item: int = 0,
    item_count: int | None = None,
) -> MeshDrawSpec:
    """Map a logical item range onto a :class:`MeshDrawSpec`.

    :param info: Mesh topology.
    :param index_count: Length of the element buffer (0 if none).
    :param vertex_count: Number of vertices.
    :param first_item: First logical item (atom, bond, …).
    :param item_count: Number of items; ``None`` draws the remainder.
    :return: Draw specification with counts clamped to the buffer.
    """
    first_item = max(0, int(first_item))
    epp = info.elements_per_item
    if epp is not None and int(epp) > 0:
        epp = int(epp)
        if item_count is None:
            if info.indexed and index_count > 0:
                item_count = max(0, (index_count - first_item * epp) // epp)
            elif info.vertices_per_item:
                vpi = int(info.vertices_per_item)
                item_count = max(0, (vertex_count - first_item * vpi) // vpi)
            else:
                item_count = 0
        first_index = first_item * epp
        count = int(item_count) * epp
        if info.indexed and index_count > 0:
            count = min(count, max(0, index_count - first_index))
        if count <= 0:
            return MeshDrawSpec(
                mode=info.mode,
                count=0,
                first=0,
                indexed=info.indexed,
                pointer=0,
            )
        return MeshDrawSpec(
            mode=info.mode,
            count=count,
            first=0 if info.indexed else first_index,
            indexed=info.indexed,
            pointer=first_index * _UINT32_BYTES if info.indexed else 0,
        )

    if info.indexed:
        total = int(index_count)
        first = first_item
        if item_count is None:
            count = max(0, total - first)
        else:
            count = int(item_count)
        if total > 0:
            count = min(count, max(0, total - first))
        return MeshDrawSpec(
            mode=info.mode,
            count=count,
            first=0,
            indexed=True,
            pointer=first * _UINT32_BYTES,
        )

    total = int(vertex_count)
    if item_count is None:
        count = max(0, total - first_item)
    else:
        count = int(item_count)
    if total > 0:
        count = min(count, max(0, total - first_item))
    return MeshDrawSpec(
        mode=info.mode,
        count=count,
        first=first_item,
        indexed=False,
        pointer=0,
    )
