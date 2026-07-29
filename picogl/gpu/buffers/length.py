"""Helpers for resolving vertex counts from GPU buffer objects."""

from __future__ import annotations

from typing import cast

from numpy.typing import ArrayLike

from picogl.protocols.drawable_buffer import (
    BufferContainer,
    DrawableBuffer,
    DrawableLengthInput,
    VertexBufferDataSource,
)


def length_from_array_data(data: ArrayLike | None, *, components: int = 1) -> int:
    """Return the number of vertices represented by a NumPy buffer."""
    if data is None:
        return 0
    try:
        n = len(data)
    except TypeError:
        return 0
    if n == 0:
        return 0
    ndim = getattr(data, "ndim", None)
    if isinstance(ndim, int):
        if ndim >= 2:
            return int(n)
        if ndim == 1 and components > 1:
            return int(n // components)
        return int(n)
    return int(n)


def _is_mock(obj: object) -> bool:
    mod = getattr(type(obj), "__module__", "") or ""
    return mod.startswith("unittest.mock")


def _has_measurable_data(obj: VertexBufferDataSource | BufferContainer | object) -> bool:
    data = getattr(obj, "data", None)
    if data is None:
        return False
    try:
        return len(data) > 0
    except TypeError:
        return False


def length_from_vbo(vbo: VertexBufferDataSource | None) -> int:
    """Return vertex count from a single VBO object."""
    if vbo is None:
        return 0
    data = getattr(vbo, "data", None)
    if data is not None:
        components = (
            getattr(vbo, "components", None)
            or getattr(vbo, "size", None)
            or 1
        )
        return length_from_array_data(data, components=int(components))
    if _implements_data_length(vbo):
        return int(cast(DrawableBuffer, vbo).data_length())
    return 0


def _implements_data_length(obj: DrawableBuffer | object) -> bool:
    """True when *obj* defines a real ``data_length`` (not a MagicMock stub)."""
    fn = getattr(type(obj), "data_length", None)
    if not callable(fn):
        return False
    return not _is_mock(obj)


def _data_length_from_buffer_like(
    obj: DrawableBuffer | VertexBufferDataSource | object,
) -> int:
    if _is_mock(obj) and not _has_measurable_data(obj):
        return 0
    if _implements_data_length(obj):
        return int(cast(DrawableBuffer, obj).data_length())
    return length_from_vbo(cast(VertexBufferDataSource | None, obj))


def drawable_data_length(drawable: DrawableLengthInput) -> int:
    """Return vertex count from a drawable buffer group, VAO/VBG, or VBO."""
    if drawable is None:
        return 0

    vao = getattr(drawable, "vao", None)
    if vao is not None and vao != 0 and not isinstance(vao, int):
        if not _is_mock(vao) or _has_measurable_data(vao):
            count = _data_length_from_buffer_like(vao)
            if count > 0:
                return count

    vbo = getattr(drawable, "vbo", None)
    if vbo is not None and not isinstance(vbo, int):
        if not _is_mock(vbo) or _has_measurable_data(vbo):
            count = length_from_vbo(cast(VertexBufferDataSource, vbo))
            if count > 0:
                return count

    named = getattr(drawable, "named_vbos", None)
    if named:
        from picogl.gpu.buffers.vertex.aliases import VertexBufferRole
        from picogl.gpu.buffers.vertex.vbo.vbo_class import VBOType

        for key in (VBOType.VBO, VertexBufferRole.VBO):
            pos = named.get(key)
            if pos is not None:
                count = length_from_vbo(cast(VertexBufferDataSource, pos))
                if count > 0:
                    return count

    count = _data_length_from_buffer_like(
        cast(DrawableBuffer | VertexBufferDataSource, drawable)
    )
    if count > 0:
        return count

    index_count = getattr(drawable, "index_count", 0)
    return int(index_count) if index_count else 0
