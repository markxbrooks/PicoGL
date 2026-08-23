"""Legacy OpenGL enums (clip planes, matrix modes, primitives, display lists)."""

from .cliping import GLLegacyClipPlane
from .list_mode import GLLegacyListMode
from .matrix_mode import GLLegacyMatrixMode
from .primitive import GLLegacyPrimitive

__all__ = [
    "GLLegacyClipPlane",
    "GLLegacyListMode",
    "GLLegacyMatrixMode",
    "GLLegacyPrimitive",
]
