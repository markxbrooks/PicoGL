"""
GL Polygon Mode
"""

from enum import IntEnum

from OpenGL.GL import GL_FILL, glPolygonMode, GL_LINE

from picogl.state.fill import GLFace, GLFillMode


class PolygonMode(IntEnum):
    """Polygon Mode"""

    FILL = GL_FILL
    LINE = GL_LINE


def set_polygon_mode_fill() -> None:
    """Ensure secondary structure is always rendered as filled polygons"""
    glPolygonMode(GLFace.FRONT_AND_BACK, GLFillMode.FILL)
