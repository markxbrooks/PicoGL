"""
GL Clear commands
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glClear, glClearColor

from picogl.backend.gl.enums import GLBitMask


def gl_clear_color(color: tuple[float, float, float, float]) -> None:
    """gl clear color"""
    glClearColor(*color)


def gl_clear(mask: GLBitMask) -> None:
    """gl clear"""
    glClear(mask)
