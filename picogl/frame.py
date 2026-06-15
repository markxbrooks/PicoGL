"""
Prepare viewport
"""

import platform

from OpenGL.raw.GL.VERSION.GL_3_2 import GL_PROGRAM_POINT_SIZE

from picogl.backend.GL.backend import GLBackend


def prepare_viewport(width: int, height: int, backend: GLBackend) -> None:
    """
    prepare

    :param width: int
    :param height: int
    :param backend: GLBackend
    :return: None

    Prepares an OpenGL Frame Viewport
    """
    if platform.system() == "Darwin":
        dpr = 2  # macOS Retina displays
    else:
        dpr = 1
    backend.viewport(0, 0, width * dpr, height * dpr)
    backend.enable_depth_test()
    backend.set_clear_color((0.1, 0.1, 0.1, 1.0))
    backend.enable(GL_PROGRAM_POINT_SIZE)
    backend.clear_background()
