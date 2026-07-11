"""
A module for OpenGL draw operations using PicoGL-specific enumerations or raw gl constants.

This module provides functions to issue OpenGL draw calls, including support for
custom draw modes and index types. It simplifies the process of working with OpenGL by
handling conversion between PicoGL enums and raw gl constants, as well as managing pointer
data for indexed draw.

Functions:
- gl_draw_arrays: Wrapper for glDrawArrays supporting PicoGL enums or raw gl constants.
- gl_draw_elements: Wrapper for glDrawElements with support for custom index pointers or offsets.
"""

from __future__ import annotations

import ctypes
from enum import Enum
from typing import Any

import numpy as np


def gl_enum(value: Any) -> Any:
    """gl enum"""
    if isinstance(value, Enum):
        return value.value
    return value


def draw_pointer(pointer: Any | None, offset: int) -> Any:
    """draw pointer"""
    if pointer is None:
        return ctypes.c_void_p(offset)
    if isinstance(pointer, list):
        return np.asarray(pointer, dtype=np.uint32)
    return pointer


