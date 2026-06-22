"""
glVertexAttribPointer wrapper.
"""

import ctypes
from typing import Any, Optional

from OpenGL.GL import glVertexAttribPointer

from picogl.boolean import GLBoolean
from picogl.core.enums.numerical import GLNumeric


def _resolve_attrib_pointer(offset: Any) -> Any:
    """Accept ``None``, byte offset ints, or an existing ``c_void_p``."""
    if offset is None:
        return None
    if isinstance(offset, ctypes.c_void_p):
        return offset
    return ctypes.c_void_p(offset)


def gl_vertex_attrib_pointer(
    index: int,
    size: int,
    num_type: GLNumeric = GLNumeric.FLOAT,
    normalized: GLBoolean = GLBoolean.FALSE,
    stride: int = 0,
    offset: Optional[Any] = None,
) -> None:
    """
    Issue ``glVertexAttribPointer``.

    *offset* may be a byte offset (``int``), ``None``, or a ``ctypes.c_void_p``.
    """
    assert index >= 0
    glVertexAttribPointer(
        index,
        size,
        num_type,
        normalized,
        stride,
        _resolve_attrib_pointer(offset),
    )
