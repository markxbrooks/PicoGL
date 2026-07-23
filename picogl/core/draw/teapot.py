"""
Draw the teapot using built-in GLUT primitives.
"""

from backend.gl.api.color import gl_color_rgb
from backend.gl.api.enable import toggle_capability, gl_enable
from backend.gl.api.polygon_mode import gl_polygon_mode
from backend.gl.capability import GLFixedFunctionCapability, GLMaterialFace
from backend.gl.state.fill import GLFillMode
from backend.glut import glut_solid_teapot
from core.rgbcolor import RGBColor


def draw_teapot(wireframe_mode):
    """Draw the teapot using built-in OpenGL primitives."""
    # Set polygon mode
    if wireframe_mode:
        fill_mode = GLFillMode.LINE
        color = RGBColor.RED # Red WireFrame
    else:
        fill_mode = GLFillMode.FILL
        color = RGBColor(0.8, 0.2, 0.2)  # Red teapot
    gl_color_rgb(color)
    toggle_capability(
        enabled=not wireframe_mode,
        capability=GLFixedFunctionCapability.LIGHTING,
    )
    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, fill_mode)
    # Draw the teapot
    glut_solid_teapot(1.0)

    # Reset polygon mode
    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
    gl_enable(GLFixedFunctionCapability.LIGHTING)