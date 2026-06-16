"""
Enable points rendering state
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import (
    glBlendFunc,
    glEnable,
)
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_POINT_SPRITE, GL_VERTEX_PROGRAM_POINT_SIZE
from OpenGL.raw.GL.VERSION.GL_3_2 import GL_PROGRAM_POINT_SIZE
from picogl.backend.capability import GLBlendFactor, GLPipelineCapability


def enable_points_rendering_state() -> None:
    """
    enable_points_rendering_state

    :return: None
    """
    glEnable(GLPipelineCapability.BLEND)
    glBlendFunc(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)
    glEnable(GL_PROGRAM_POINT_SIZE)
    glEnable(GL_POINT_SPRITE)
    glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
