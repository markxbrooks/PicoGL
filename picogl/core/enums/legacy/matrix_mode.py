from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_PROJECTION, GL_MODELVIEW


class GLLegacyMatrixMode(IntEnum):
    """gl Matrix Mode"""

    PROJECTION = GL_PROJECTION
    MODELVIEW = GL_MODELVIEW