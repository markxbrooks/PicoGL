"""
Numerical gl Values
"""

from enum import IntEnum

from OpenGL.raw.GL._types import GL_FALSE, GL_TRUE

_SUPPORTED_BOOLEAN_TYPES = {
    GL_FALSE,
    GL_TRUE,
}


class GLBoolean(IntEnum):
    """gl Boolean Values"""

    FALSE = GL_FALSE
    TRUE = GL_TRUE

    @classmethod
    def supported_gl_types(cls):
        return [m.value for m in cls if m.value in _SUPPORTED_BOOLEAN_TYPES]

    @classmethod
    def choices(cls):
        return [m.value for m in cls]
