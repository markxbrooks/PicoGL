"""
Prepare viewport
"""

import platform

from OpenGL.raw.GL.VERSION.GL_3_2 import GL_PROGRAM_POINT_SIZE
from picogl.backend.gl.backend import GLBackend
from picogl.backend.gl.enums import GLBitMask


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
    backend.frame.viewport(0, 0, width * dpr, height * dpr)
    backend.depth.set_depth_test(True)
    backend.frame.set_clear_color((0.1, 0.1, 0.1, 1.0))
    backend.capabilities.enable(GL_PROGRAM_POINT_SIZE)
    backend.frame.clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
