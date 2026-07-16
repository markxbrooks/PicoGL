"""Legacy display list wrappers."""

from __future__ import annotations

from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_COMPILE, glEndList, glGenLists,
                                          glNewList)


class GLLegacyListMode(IntEnum):
    """Display list compilation mode."""

    COMPILE = GL_COMPILE


def gl_gen_lists(range_: int = 1) -> int:
    """Generate contiguous empty display lists."""
    return glGenLists(range_)


def gl_new_list(list_: int, mode: GLLegacyListMode | int = GLLegacyListMode.COMPILE) -> None:
    """Begin compiling a display list."""
    glNewList(list_, int(mode))


def gl_end_list() -> None:
    """End compiling a display list."""
    glEndList()
