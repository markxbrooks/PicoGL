"""
Lighting setup functions.
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_LESS, gl_enable, glClearColor,
                                          glDepthFunc)

from picogl.backend.gl.api.clear import gl_clear_rgba_color
from picogl.backend.gl.api.depth import gl_depth_func
from picogl.backend.gl.glfunc import GLDepthFunc
from picogl.core.rgbcolor import RGBAColor
from picogl.core.setup import gl_setup_depth_test


def gl_initialize_background(bg_color = RGBAColor(0.0, 0, 0.4, 0)) -> None:
    """
    initialize_background

    :param: bg_color: RGBAColor
    :return: None
    """
    gl_setup_depth_test()
    gl_depth_func(GLDepthFunc.LESS)
    gl_clear_rgba_color(bg_color)
