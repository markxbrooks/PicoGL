"""
GL Client State
"""
from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_1 import (GL_COLOR_ARRAY, GL_NORMAL_ARRAY,
                                          GL_TEXTURE_COORD_ARRAY,
                                          GL_VERTEX_ARRAY)


class GLClientState(IntEnum):
    """Enum defining GLClientState enums"""
    VERTEX = GL_VERTEX_ARRAY
    NORMAL = GL_NORMAL_ARRAY
    COLOR = GL_COLOR_ARRAY
    TEXCOORD = GL_TEXTURE_COORD_ARRAY
