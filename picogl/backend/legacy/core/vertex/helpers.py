"""
GL Clear Buffers
"""
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_DEPTH_TEST, GL_MODELVIEW,
                                          glEnable, glLoadIdentity,
                                          glMatrixMode)
from OpenGL.raw.GL.VERSION.GL_1_3 import GL_MULTISAMPLE
from picogl.buffers.glframe import GLFramebuffer


def gl_clear_buffers() -> None:
    """
    gl_clear_buffers

    Clears the color_array and depth atoms_buffers and resets modelview matrix.
    """
    glMatrixMode(GL_MODELVIEW)  # Legacy pipeline
    glLoadIdentity()  # Reset modelview matrix
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    buffer = GLFramebuffer()
    buffer.clear(color=(0.0, 0.0, 0.0, 1.0))
