"""Legacy display-list compilation mode enum."""

from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_COMPILE


class GLLegacyListMode(IntEnum):
    """Display list compilation mode."""

    COMPILE = GL_COMPILE
