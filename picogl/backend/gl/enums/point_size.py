"""
GL Point size Enums
"""

from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POINT_SMOOTH
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_POINT_SPRITE, GL_VERTEX_PROGRAM_POINT_SIZE
from OpenGL.raw.GL.VERSION.GL_3_2 import GL_PROGRAM_POINT_SIZE


class GLPointCapability(IntEnum):
    """Modern point rendering capabilities."""

    PROGRAM_POINT_SIZE = GL_PROGRAM_POINT_SIZE


class GLLegacyPointCapability(IntEnum):
    """Legacy / deprecated point rendering features."""

    POINT_SMOOTH = GL_POINT_SMOOTH
    POINT_SPRITE = GL_POINT_SPRITE
    VERTEX_PROGRAM_POINT_SIZE = GL_VERTEX_PROGRAM_POINT_SIZE
