"""
Enable points rendering state
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glBlendFunc, gl_enable
from OpenGL.raw.GL.VERSION.GL_3_2 import GL_PROGRAM_POINT_SIZE

from picogl.backend.gl.capability import GLBlendFactor, GLPipelineCapability


def enable_points_rendering_state() -> None:
    """Blend + shader point size for GL_POINTS (Core Profile; no GL_POINT_SPRITE)."""
    gl_enable(GLPipelineCapability.BLEND)
    glBlendFunc(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)
    gl_enable(GL_PROGRAM_POINT_SIZE)
