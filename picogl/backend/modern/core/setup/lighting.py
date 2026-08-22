from picogl.backend.gl.api.clear import gl_clear_rgba_color
from picogl.backend.gl.api.depth import gl_depth_func
from picogl.backend.gl.glfunc import GLDepthFunc
from picogl.core.rgbcolor import RGBAColor
from picogl.core.setup import gl_setup_depth_test


def gl_initialize_background(bg_color: RGBAColor = RGBAColor(0.0, 0, 0.4, 0)) -> None:
    """Enable depth test, set depth func, and set the clear color."""
    gl_setup_depth_test()
    gl_depth_func(GLDepthFunc.LESS)
    gl_clear_rgba_color(bg_color)
