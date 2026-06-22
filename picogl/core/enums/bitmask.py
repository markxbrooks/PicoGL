from enum import IntFlag

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LINE_BIT, GL_DEPTH_BUFFER_BIT, GL_COLOR_BUFFER_BIT


class GLBitMask(IntFlag):
    """gl Bit Mask"""

    LINE = GL_LINE_BIT
    DEPTH_BUFFER = GL_DEPTH_BUFFER_BIT
    COLOR_BUFFER = GL_COLOR_BUFFER_BIT