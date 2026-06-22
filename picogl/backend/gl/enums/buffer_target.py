"""
Provides an enumeration for OpenGL buffer targets.

This module defines the GLBufferTarget enumeration that maps to various
OpenGL buffer target constants. These constants are used to specify the
target to which an OpenGL buffer object is bound.
"""

from enum import IntEnum

from OpenGL.raw.GL.ARB.shader_storage_buffer_object import \
    GL_SHADER_STORAGE_BUFFER
from OpenGL.raw.GL.VERSION.GL_1_5 import (GL_ARRAY_BUFFER,
                                          GL_ELEMENT_ARRAY_BUFFER)
from OpenGL.raw.GL.VERSION.GL_3_1 import GL_UNIFORM_BUFFER


class GLBufferTarget(IntEnum):
    """gl Buffer Target"""

    ARRAY = GL_ARRAY_BUFFER
    ELEMENT = GL_ELEMENT_ARRAY_BUFFER
    UNIFORM = GL_UNIFORM_BUFFER
    SHADER_STORAGE = GL_SHADER_STORAGE_BUFFER
