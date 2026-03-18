"""
Enable points rendering state
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_BLEND, GL_ONE_MINUS_SRC_ALPHA,
                                          GL_SRC_ALPHA, glBlendFunc, glEnable)
from OpenGL.raw.GL.VERSION.GL_2_0 import (GL_POINT_SPRITE,
                                          GL_VERTEX_PROGRAM_POINT_SIZE)
from OpenGL.raw.GL.VERSION.GL_3_2 import GL_PROGRAM_POINT_SIZE


def enable_points_rendering_state() -> None:
    """
    enable_points_rendering_state

    :return: None
    """
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_PROGRAM_POINT_SIZE)
    glEnable(GL_POINT_SPRITE)
    glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
