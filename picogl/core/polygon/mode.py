"""
gl Polygon Mode
"""

from OpenGL.GL import glPolygonMode
from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.state.fill import GLFillMode


def gl_polygon_mode(face: GLMaterialFace, mode: GLFillMode):
    """gl polygon mode"""
    glPolygonMode(face, mode)


def set_polygon_mode_fill() -> None:
    """Ensure secondary structure is always rendered as filled polygons"""
    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)


def set_polygon_mode_line() -> None:
    """Render polygons as wireframe outlines."""
    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)


def gl_set_line_mode():
    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)


def gl_set_polygon_mode():
    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)
