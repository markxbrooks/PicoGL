"""
GL Fill Mode
"""

from enum import IntEnum

from OpenGL.GL import GL_FILL, GL_LINE, GL_POINT, GL_FRONT, GL_BACK, GL_FRONT_AND_BACK


class Selectable:
    """Selectable"""

    @classmethod
    def choices(cls):
        return [m.value for m in cls]

    @classmethod
    def from_value(cls, value: int):
        return cls(value)


class GLFace(Selectable, IntEnum):
    """GL Face"""
    FRONT = GL_FRONT
    BACK = GL_BACK
    FRONT_AND_BACK = GL_FRONT_AND_BACK


class GLFillMode(Selectable, IntEnum):
    """GL Fill Mode"""
    FILL = GL_FILL
    LINE = GL_LINE
    POINT = GL_POINT
