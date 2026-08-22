"""
gl Polygon Mode
"""

from OpenGL.GL import glPolygonMode

from picogl.backend.gl.state.fill import GLFace, GLFillMode


def gl_polygon_mode(face: GLFace, mode: GLFillMode):
    """gl polygon mode"""
    glPolygonMode(face, mode)


def set_polygon_mode_fill() -> None:
    """Ensure secondary structure is always rendered as filled polygons"""
    gl_polygon_mode(GLFace.FRONT_AND_BACK, GLFillMode.FILL)


def set_polygon_mode_line() -> None:
    """Render polygons as wireframe outlines."""
    gl_polygon_mode(GLFace.FRONT_AND_BACK, GLFillMode.LINE)
