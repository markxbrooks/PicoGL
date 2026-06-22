"""
Enable points rendering state
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glBlendFunc, glEnable
from OpenGL.raw.GL.VERSION.GL_3_2 import GL_PROGRAM_POINT_SIZE

from picogl.backend.gl.capability import GLBlendFactor, GLPipelineCapability


def enable_points_rendering_state() -> None:
    """Blend + shader point size for GL_POINTS (Core Profile; no GL_POINT_SPRITE)."""
    glEnable(GLPipelineCapability.BLEND)
    glBlendFunc(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)
    glEnable(GL_PROGRAM_POINT_SIZE)
