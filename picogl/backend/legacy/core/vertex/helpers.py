"""
GL Clear Buffers
"""
from OpenGL.GL import (GL_DEPTH_TEST, GL_MODELVIEW, GL_MULTISAMPLE,
                                          glEnable, glLoadIdentity,
                                          glMatrixMode, glClearColor, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glClear)


def gl_clear_buffers() -> None:
    """
    gl_clear_buffers

    Clears the color_array and depth atoms_buffers and resets modelview matrix.
    """
    glMatrixMode(GL_MODELVIEW)  # Legacy pipeline
    glLoadIdentity()  # Reset modelview matrix
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    # backend = GLBackend()
    color = (0.0, 0.0, 0.0, 1.0)
    glClearColor(*color)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)