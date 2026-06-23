"""
Enable Smoothing
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_LINE_SMOOTH,
    GL_LINE_SMOOTH_HINT,
    GL_NICEST,
    GL_POINT_SMOOTH,
    GL_POINT_SMOOTH_HINT,
    gl_enable,
    glHint,
)


def enable_smoothing() -> None:
    """
    enable_smoothing

    :return: None
    setup smoothing in legacy picogl
    """
    gl_enable(GL_POINT_SMOOTH)
    gl_enable(GL_LINE_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
