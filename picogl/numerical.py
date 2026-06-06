"""
Numerical GL Values
"""

from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_BYTE, GL_DOUBLE, GL_FLOAT, GL_INT,
                                          GL_SHORT, GL_UNSIGNED_BYTE,
                                          GL_UNSIGNED_INT, GL_UNSIGNED_SHORT)


_SUPPORTED_VERTEX_POINTER_TYPES = {
    GL_FLOAT,
    GL_DOUBLE,
    GL_INT,
    GL_SHORT,
    GL_BYTE,
}


class GLNumeric(IntEnum):
    """GL Numerical Values"""
    FLOAT = GL_FLOAT
    DOUBLE = GL_DOUBLE
    INT = GL_INT
    UNSIGNED_INT = GL_UNSIGNED_INT
    SHORT = GL_SHORT
    UNSIGNED_SHORT = GL_UNSIGNED_SHORT
    BYTE = GL_BYTE
    UNSIGNED_BYTE = GL_UNSIGNED_BYTE

    @classmethod
    def supported_gl_types(cls):
        return [m.value for m in cls if m.value in _SUPPORTED_VERTEX_POINTER_TYPES]

    @classmethod
    def choices(cls):
        return [m.value for m in cls]
