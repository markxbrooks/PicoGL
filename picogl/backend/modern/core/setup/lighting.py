from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LESS, gl_enable, glClearColor, glDepthFunc
from picogl.backend.gl.capability import GLPipelineCapability


def initialize_background() -> None:
    """
    initialize_background

    :return: None
    """
    gl_enable(GLPipelineCapability.DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(0.0, 0, 0.4, 0)
