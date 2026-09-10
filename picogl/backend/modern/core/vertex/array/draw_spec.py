"""
Draw spec
"""
import ctypes
from dataclasses import dataclass

from backend.gl.enums import GLDrawMode, GLIndexType


@dataclass(frozen=True, slots=True)
class DrawSpec:
    """DrawSpec class"""
    mode: int = GLDrawMode.POINTS
    count: int | None = None
    dtype: int = GLIndexType.UNSIGNED_INT
    pointer: int | ctypes.c_void_p | None = ctypes.c_void_p(0)
    first: int = 0