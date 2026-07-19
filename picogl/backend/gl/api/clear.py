"""
GL Clear commands
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glClear, glClearColor

from picogl.backend.gl.enums import GLBitMask
from picogl.core.rgbcolor import RGBAColor


def gl_clear_color(color: tuple[float, float, float, float]) -> None:
    """gl clear color"""
    glClearColor(*color)


def gl_clear_rgba_color(rgba_color: RGBAColor) -> None:
    """gl clear rgba color"""
    gl_clear_color(*rgba_color.tuple)


def gl_clear(mask: GLBitMask) -> None:
    """gl clear"""
    glClear(mask)
