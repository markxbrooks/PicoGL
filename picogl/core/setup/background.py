from picogl.backend.gl.api.clear import gl_clear_rgba_color
from picogl.core.rgbcolor import RGBAColor


def gl_setup_background_color():
    gl_clear_rgba_color(RGBAColor.BLACK)
