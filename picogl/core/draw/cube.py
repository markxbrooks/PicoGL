"""
draw fallback cube
"""


from picogl.backend.gl.api.color import gl_color_rgb
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.state.fill import GLFillMode
from picogl.backend.gl.state.scoped import gl_disabled
from picogl.backend.glut.cube import glut_wire_cube
from picogl.core.rgbcolor import RGBColor
from picogl.polygon.mode import gl_polygon_mode_context


def draw_fallback_cube(self):
    """Draw a simple wireframe cube as fallback."""
    with gl_disabled(GLFixedFunctionCapability.LIGHTING):
        with gl_polygon_mode_context(GLFillMode.LINE):
            gl_color_rgb(RGBColor(1.0, 0.0, 0.0))
            glut_wire_cube(2.0)
