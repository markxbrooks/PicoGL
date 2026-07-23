"""
draw fallback cube
"""

from picogl.backend.gl.api.color import gl_color_rgb
from picogl.backend.gl.api.enable import gl_enable
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.state.fill import (
                                          GLFillMode)
from picogl.backend.glut.cube import glut_wire_cube
from picogl.core.rgbcolor import RGBColor
from polygon.mode import gl_polygon_mode_context


def draw_fallback_cube(self):
    """Draw a simple wireframe cube as fallback."""
    gl_disable(GLFixedFunctionCapability.LIGHTING)
    red_rgb = RGBColor(1.0, 0.0, 0.0)
    gl_color_rgb(red_rgb)  # Red wireframe
    with gl_polygon_mode_context(GLFillMode.LINE):
        glut_wire_cube(2.0)
    with gl_polygon_mode_context(GLFillMode.FILL):
        gl_enable(GLFixedFunctionCapability.LIGHTING)