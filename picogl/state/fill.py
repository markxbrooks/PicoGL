"""
GL Fill Mode
"""

from enum import IntEnum

from OpenGL.GL import GL_BACK, GL_FILL, GL_FRONT, GL_FRONT_AND_BACK, GL_LINE, GL_POINT, GL_LIGHT0, GL_LIGHT1, GL_LIGHTING, GL_AMBIENT_AND_DIFFUSE, GL_POSITION, GL_AMBIENT, GL_DIFFUSE, GL_SPECULAR
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_COLOR_MATERIAL


class Selectable:
    """Selectable"""

    @classmethod
    def choices(cls):
        return [m.value for m in cls]

    @classmethod
    def from_value(cls, value: int):
        return cls(value)


class GLLight(Selectable, IntEnum):
    """GL Lighting"""
    LIGHTING = GL_LIGHTING
    LIGHT0 = GL_LIGHT0
    LIGHT1 = GL_LIGHT1


class GLCapability(IntEnum):
    COLOR_MATERIAL = GL_COLOR_MATERIAL


class GLMaterialParameter(IntEnum):
    AMBIENT = GL_AMBIENT
    DIFFUSE = GL_DIFFUSE
    SPECULAR = GL_SPECULAR


class GLColorMaterialMode(IntEnum):
    AMBIENT_AND_DIFFUSE = GL_AMBIENT_AND_DIFFUSE


class GLLightParameter(IntEnum):
    POSITION = GL_POSITION
    AMBIENT = GL_AMBIENT
    DIFFUSE = GL_DIFFUSE
    SPECULAR = GL_SPECULAR


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
