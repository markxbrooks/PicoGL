"""
GL Blend Driver
"""

from OpenGL.GL import (
    GL_BLEND,
    glBlendFunc, glGetIntegerv
)

from picogl.backend.GL.driver.capability import GLCapabilityDriver
from picogl.backend.capability import GLBlendTarget, GLBlendFactor, GLPipelineCapability
from picogl.backend.state import gl_value
from picogl.state.fill import GLCapability


class GLBlendDriver:
    """
    GLBlendDriver
    """

    def __init__(self, capabilities: GLCapabilityDriver):
        self.capabilities = capabilities

    def set_blend(self, enabled: bool):
        self.capabilities.set_enabled(GLPipelineCapability.BLEND, enabled)

    @staticmethod
    def set_blend_func(src: GLBlendFactor, dst: GLBlendFactor):
        glBlendFunc(gl_value(src), gl_value(dst))

    @staticmethod
    def get_blend_func() -> tuple[GLBlendFactor, GLBlendFactor]:
        src = GLBlendFactor.from_gl(int(glGetIntegerv(GLBlendTarget.BLEND_SRC)))
        dst = GLBlendFactor.from_gl(int(glGetIntegerv(GLBlendTarget.BLEND_DST)))
        return src, dst

    def setup_blending(self):
        self.set_blend_func(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)


class GLBlendDriverOld:
    """Blend capability and blend-function operations."""

    def __init__(self, capabilities: GLCapabilityDriver):
        self.capabilities = capabilities

    def set_blend(self, enabled: bool):
        self.capabilities.set_enabled(GL_BLEND, enabled)

    @staticmethod
    def set_blend_func(src: GLBlendFactor, dst: GLBlendFactor) -> None:
        glBlendFunc(gl_value(src), gl_value(dst))

    def setup_blending(self):
        self.set_blend_func(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)

    @staticmethod
    def get_blend_func() -> tuple[int, int]:
        return int(glGetIntegerv(GLBlendTarget.BLEND_SRC)), int(glGetIntegerv(GLBlendTarget.BLEND_DST))
