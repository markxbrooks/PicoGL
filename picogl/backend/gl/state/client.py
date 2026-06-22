"""Enumeration for representing OpenGL client states.

This module defines an enumeration for the OpenGL client states used in rendering operations.
These states specify different types of vertex array data that can be enabled or disabled
in an OpenGL context.
"""

from enum import IntEnum

from OpenGL.GL import (GL_COLOR_ARRAY, GL_NORMAL_ARRAY, GL_TEXTURE_COORD_ARRAY,
                       GL_VERTEX_ARRAY)


class GLClientState(IntEnum):
    """Enum defining GLClientState enums"""

    VERTEX = GL_VERTEX_ARRAY
    NORMAL = GL_NORMAL_ARRAY
    COLOR = GL_COLOR_ARRAY
    TEXCOORD = GL_TEXTURE_COORD_ARRAY
