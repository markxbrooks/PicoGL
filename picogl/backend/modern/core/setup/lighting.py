from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LESS, glClearColor, glDepthFunc, glEnable

from picogl.backend.capability import GLPipelineCapability


def initialize_background() -> None:
    """
    initialize_background

    :return: None
    """
    glEnable(GLPipelineCapability.DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(0.0, 0, 0.4, 0)
