"""
Provides OpenGL utilities for handling attribute pointers.

This module defines utility functions for working with attribute pointers,
specifically for managing OpenGL attribute pointers like `glVertexAttribPointer`.
It includes internal helper functions for resolving pointer offsets.

Functions:
- gl_vertex_attrib_pointer: Wraps the OpenGL function `glVertexAttribPointer`.

"""

import ctypes
from typing import Any, Optional

from OpenGL.GL import glVertexAttribPointer

from picogl.backend.gl.enums import GLNumeric
from picogl.boolean import GLBoolean


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
