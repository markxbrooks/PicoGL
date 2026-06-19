"""OpenGL draw wrappers."""

from __future__ import annotations

import ctypes
from enum import Enum
from typing import Any

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays, glDrawElements

from picogl.state.draw_mode import GLDrawMode, GLIndexType


def _gl_enum(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


def _draw_pointer(pointer: Any | None, offset: int) -> Any:
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
    """Issue ``glDrawArrays`` with PicoGL draw-mode enums or raw GL constants."""
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
