"""
A module for OpenGL draw operations using PicoGL-specific enumerations or raw gl constants.

This module provides functions to issue OpenGL draw calls, including support for
custom draw modes and index types. It simplifies the process of working with OpenGL by
handling conversion between PicoGL enums and raw gl constants, as well as managing pointer
data for indexed drawing.

Functions:
- gl_draw_arrays: Wrapper for glDrawArrays supporting PicoGL enums or raw gl constants.
- gl_draw_elements: Wrapper for glDrawElements with support for custom index pointers or offsets.
"""

from __future__ import annotations

import ctypes
from enum import Enum
from typing import Any

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays, glDrawElements

from picogl.core.enums.draw_mode import GLDrawMode
from picogl.core.enums.index_type import GLIndexType


def _gl_enum(value: Any) -> Any:
    """gl enum"""
    if isinstance(value, Enum):
        return value.value
    return value


def _draw_pointer(pointer: Any | None, offset: int) -> Any:
    """draw pointer"""
    if pointer is None:
        return ctypes.c_void_p(offset)
    if isinstance(pointer, list):
        return np.asarray(pointer, dtype=np.uint32)
    return pointer


def gl_draw_arrays(
    index_count: int,
    mode: GLDrawMode | int,
    first: int = 0,
) -> None:
    """Issue ``glDrawArrays`` with PicoGL draw-mode enums or raw gl constants."""
    assert mode is not None
    glDrawArrays(_gl_enum(mode), int(first), int(index_count))


def gl_draw_elements(
    index_count: int,
    dtype: int | None = GLIndexType.UNSIGNED_INT,
    mode: GLDrawMode | int | None = GLDrawMode.TRIANGLES,
    pointer: Any | None = None,
    offset: int = 0,
) -> None:
    """
    Issue ``glDrawElements``.

    *pointer* may be a client index array, ``None`` (EBO bound), or omitted to use *offset*.
    """
    assert dtype is not None
    assert mode is not None
    pointer = _draw_pointer(pointer, offset)
    glDrawElements(
        _gl_enum(mode),
        int(index_count),
        _gl_enum(dtype),
        pointer,
    )
