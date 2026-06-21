"""
GL Polygon Mode
"""

from OpenGL.GL import glPolygonMode

from picogl.state.fill import GLFace, GLFillMode


def gl_polygon_mode(face: GLFace, mode: GLFillMode):
    """GL polygon mode"""
    glPolygonMode(face, mode)


def set_polygon_mode_fill() -> None:
    """Ensure secondary structure is always rendered as filled polygons"""
    gl_polygon_mode(GLFace.FRONT_AND_BACK, GLFillMode.FILL)
