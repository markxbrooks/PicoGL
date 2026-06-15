"""
GL Polygon Mode
"""
from enum import Enum

from OpenGL.GL import GL_FILL, GL_FRONT_AND_BACK, glPolygonMode
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_FILL, GL_LINE


def set_polygon_mode_fill() -> None:
    """Ensure secondary structure is always rendered as filled polygons"""
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


class PolygonMode(Enum):
    """Polygon Mode"""
    FILL = GL_FILL
    LINE = GL_LINE