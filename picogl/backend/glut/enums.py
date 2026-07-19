"""GLUT display-mode and related constants."""

from enum import IntFlag

from OpenGL.GLUT import GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGBA


class GLUTDisplayMode(IntFlag):
    """Flags for :func:`~picogl.backend.glut.init.glut_init_display_mode`."""

    RGBA = int(GLUT_RGBA)
    DOUBLE = int(GLUT_DOUBLE)
    DEPTH = int(GLUT_DEPTH)
