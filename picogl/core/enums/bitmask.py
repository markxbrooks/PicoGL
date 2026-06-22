"""
This module defines the `GLBitMask` enumeration for representing OpenGL bit
masks using the `IntFlag` class from the `enum` module.

The `GLBitMask` enumeration provides symbolic names for specific OpenGL
bitmask values, enabling easier interaction with OpenGL constants defined
in the `GL_1_0` version of the OpenGL library.
"""

from enum import IntFlag

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LINE_BIT, GL_DEPTH_BUFFER_BIT, GL_COLOR_BUFFER_BIT


class GLBitMask(IntFlag):
    """gl Bit Mask"""

    LINE = GL_LINE_BIT
    DEPTH_BUFFER = GL_DEPTH_BUFFER_BIT
    COLOR_BUFFER = GL_COLOR_BUFFER_BIT