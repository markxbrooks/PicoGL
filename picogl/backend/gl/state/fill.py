"""
gl Fill Mode
"""

from enum import IntEnum

from OpenGL.GL import (GL_AMBIENT, GL_AMBIENT_AND_DIFFUSE, GL_BACK, GL_DIFFUSE,
                       GL_FILL, GL_FRONT, GL_FRONT_AND_BACK, GL_LIGHT0,
                       GL_LIGHT1, GL_LIGHTING, GL_LINE, GL_POINT, GL_POSITION,
                       GL_SPECULAR)
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_COLOR_MATERIAL, GL_SHININESS
from OpenGL.raw.GL.VERSION.GL_3_0 import GL_CLIP_DISTANCE0, GL_CLIP_DISTANCE1


class Selectable:
    """Selectable"""

    @classmethod
    def choices(cls):
        return [m.value for m in cls]

    @classmethod
    def from_value(cls, value: int):
        return cls(value)


class GLLight(Selectable, IntEnum):
    """gl Lighting"""

    LIGHTING = GL_LIGHTING
    LIGHT0 = GL_LIGHT0
    LIGHT1 = GL_LIGHT1


class GLCapability(IntEnum):
    """gl Capability"""

    COLOR_MATERIAL = GL_COLOR_MATERIAL
    CLIP_DISTANCE0 = GL_CLIP_DISTANCE0
    CLIP_DISTANCE1 = GL_CLIP_DISTANCE1


class GLColorMaterialMode(IntEnum):
    """gl Color Material Mode"""

    AMBIENT_AND_DIFFUSE = GL_AMBIENT_AND_DIFFUSE


class GLLightParameter(IntEnum):
    """gl Light Parameter"""

    POSITION = GL_POSITION
    AMBIENT = GL_AMBIENT
    DIFFUSE = GL_DIFFUSE
    SPECULAR = GL_SPECULAR
    SHININESS = GL_SHININESS


class GLFace(Selectable, IntEnum):
    """gl Face"""

    FRONT = GL_FRONT
    BACK = GL_BACK
    FRONT_AND_BACK = GL_FRONT_AND_BACK


class GLFillMode(Selectable, IntEnum):
    """gl Fill Mode"""

    FILL = GL_FILL
    LINE = GL_LINE
    POINT = GL_POINT
