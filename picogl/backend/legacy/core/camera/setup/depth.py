"""
Enable depth test
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_DEPTH_TEST, glClearDepth, gl_enable


def enable_depth_test() -> None:
    """
    enable_depth_test

    :return: None
    """
    gl_enable(GL_DEPTH_TEST)
    glClearDepth(1.0)
