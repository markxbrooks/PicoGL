"""
GL Fill Mode
"""

from enum import IntEnum

from OpenGL.GL import GL_FILL, GL_LINE, GL_POINT


class GLFillMode(IntEnum):
    """GL Fill Mode"""
    FILL = GL_FILL
    LINE = GL_LINE
    POINT = GL_POINT

    @classmethod
    def choices(cls):
        return [m.value for m in cls]

    @classmethod
    def from_value(cls, value: int):
        return cls(value)