"""
Enable depth test
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glClearDepth, glEnable
from picogl.backend.gl.capability import GLPipelineCapability


def enable_depth_test() -> None:
    """
    enable_depth_test

    :return: None
    """
    glEnable(GLPipelineCapability.DEPTH_TEST)
    glClearDepth(1.0)
