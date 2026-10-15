"""
Enumeration of OpenGL texture level parameter names.
"""

from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_1 import GL_TEXTURE_HEIGHT, GL_TEXTURE_WIDTH


class GLTexLevelParameter(IntEnum):
    """``pname`` values for ``glGetTexLevelParameteriv``."""

    WIDTH = GL_TEXTURE_WIDTH
    HEIGHT = GL_TEXTURE_HEIGHT
