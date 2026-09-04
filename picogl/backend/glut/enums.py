"""GLUT display-mode and related constants."""

from enum import IntEnum, IntFlag

from OpenGL.GLUT import (
    GLUT_DEPTH,
    GLUT_DOUBLE,
    GLUT_DOWN,
    GLUT_LEFT_BUTTON,
    GLUT_RGBA,
    GLUT_UP,
)


class GLUTDisplayMode(IntFlag):
    """Flags for :func:`~picogl.backend.glut.init.glut_init_display_mode`."""

    RGBA = int(GLUT_RGBA)
    DOUBLE = int(GLUT_DOUBLE)
    DEPTH = int(GLUT_DEPTH)


class GLUTMouseButton(IntEnum):
    """GLUT mouse button identifiers."""

    LEFT = int(GLUT_LEFT_BUTTON)
    # Common freeglut / scroll-button values (not in Apple GLUT.framework).
    WHEEL_UP = 3
    WHEEL_DOWN = 4


class GLUTMouseState(IntEnum):
    """GLUT mouse button press/release state."""

    DOWN = int(GLUT_DOWN)
    UP = int(GLUT_UP)
