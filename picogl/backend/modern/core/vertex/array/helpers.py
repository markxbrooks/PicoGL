"""
Enable points rendering state
"""

from picogl.backend.gl.capability import GLBlendFactor, GLPipelineCapability
from picogl.backend.gl.enums.point_size import GLPointCapability
from picogl.backend.gl.wrappers.blending import gl_blend_func
from picogl.backend.gl.wrappers.enable import gl_enable, gl_disable
from contextlib import contextmanager


@contextmanager
def point_rendering():
    """Temporarily configure OpenGL state for point rendering."""

    gl_enable(GLPipelineCapability.BLEND)
    gl_blend_func(
        GLBlendFactor.SRC_ALPHA,
        GLBlendFactor.ONE_MINUS_SRC_ALPHA,
    )
    gl_enable(GLPointCapability.PROGRAM_POINT_SIZE)

    try:
        yield
    finally:
        gl_disable(GLPointCapability.PROGRAM_POINT_SIZE)
        gl_disable(GLPipelineCapability.BLEND)


def configure_point_rendering() -> None:
    """Blend + shader point size for GL_POINTS (Core Profile; no GL_POINT_SPRITE)."""
    gl_enable(GLPipelineCapability.BLEND)
    gl_blend_func(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)
    gl_enable(GLPointCapability.PROGRAM_POINT_SIZE)

