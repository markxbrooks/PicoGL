"""
Enable depth test
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glClearDepth, gl_enable

from picogl.backend.gl.capability import GLPipelineCapability


def enable_depth_test() -> None:
    """
    enable_depth_test

    :return: None
    """
    gl_enable(GLPipelineCapability.DEPTH_TEST)
    glClearDepth(1.0)
