"""
Enable Smoothing
"""

from OpenGL import error as gl_error
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_LINE_SMOOTH, GL_LINE_SMOOTH_HINT,
                                          GL_NICEST, GL_POINT_SMOOTH,
                                          GL_POINT_SMOOTH_HINT)
from picogl.backend.gl.api.enable import gl_enable
from picogl.backend.gl.api.error import gl_check_errors
from picogl.backend.gl.api.hint import gl_hint


def enable_smoothing(backend: "GLBackend") -> None:
    """
    Legacy point/line smoothing (GL_POINT_SMOOTH, GL_LINE_SMOOTH).

    Omitted in OpenGL core profile (e.g. macOS): enums are invalid for gl_enable.
    """
    try:
        gl_enable(GL_POINT_SMOOTH)
        gl_enable(GL_LINE_SMOOTH)
        gl_hint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        gl_hint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    except gl_error.GLError:
        gl_check_errors()
