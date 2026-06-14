"""
Enable Smoothing
"""

from OpenGL import error as gl_error
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_LINE_SMOOTH, GL_LINE_SMOOTH_HINT,
                                          GL_NICEST, GL_POINT_SMOOTH,
                                          GL_POINT_SMOOTH_HINT, glEnable,
                                          glHint)


def enable_smoothing(backend: "GLBackend") -> None:
    """
    Legacy point/line smoothing (GL_POINT_SMOOTH, GL_LINE_SMOOTH).

    Omitted in OpenGL core profile (e.g. macOS): enums are invalid for glEnable.
    """
    try:
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    except gl_error.GLError:
        pass
