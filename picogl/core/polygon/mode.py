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


def gl_set_line_mode(
    face: GLMaterialFace = GLMaterialFace.FRONT_AND_BACK,
) -> None:
    """Convenience: filled polygons (legacy name kept for callers)."""
    gl_polygon_mode(face, GLFillMode.FILL)


def gl_set_polygon_mode(
    face: GLMaterialFace = GLMaterialFace.FRONT_AND_BACK,
    mode: GLFillMode = GLFillMode.LINE,
) -> None:
    """
    Set polygon rasterization mode.

    Defaults to wireframe (``GLFillMode.LINE``) when called with no arguments,
    matching existing zero-arg callers. Face and mode may also be passed
    explicitly (as OpenGL ``glPolygonMode`` does).
    """
    gl_polygon_mode(face, mode)
