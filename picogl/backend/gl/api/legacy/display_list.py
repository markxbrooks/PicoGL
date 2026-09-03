"""Legacy display list wrappers."""

from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_1_0 import glEndList, glGenLists, glNewList

from picogl.backend.gl.enums.legacy.list_mode import GLLegacyListMode

__all__ = ["GLLegacyListMode", "gl_end_list", "gl_gen_lists", "gl_new_list"]


def gl_gen_lists(range_: int = 1) -> int:
    """Generate contiguous empty display lists."""
    return glGenLists(range_)


def gl_new_list(
    list_: int, mode: GLLegacyListMode | int = GLLegacyListMode.COMPILE
) -> None:
    """Begin compiling a display list."""
    glNewList(list_, int(mode))


def gl_end_list() -> None:
    """End compiling a display list."""
    glEndList()
