"""OpenGL hint target / mode enums."""

from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_DONT_CARE, GL_FASTEST,
                                          GL_LINE_SMOOTH_HINT, GL_NICEST,
                                          GL_POINT_SMOOTH_HINT)


class GLHintTarget(IntEnum):
    LINE_SMOOTH = GL_LINE_SMOOTH_HINT
    POINT_SMOOTH = GL_POINT_SMOOTH_HINT


class GLHintMode(IntEnum):
    NICEST = GL_NICEST
    FASTEST = GL_FASTEST
    DONT_CARE = GL_DONT_CARE
