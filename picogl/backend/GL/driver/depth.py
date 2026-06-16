from typing import Any

from OpenGL.GL import (
    GL_LESS,
    glDepthFunc,
    glDepthMask, glGetBooleanv, GL_DEPTH_WRITEMASK,
)

from picogl.backend.GL.driver.capability import GLCapabilityDriver
from picogl.backend.capability import GLPipelineCapability


class GLDepthDriver:
    """Depth test, write mask, and depth-function operations."""

    def __init__(self, capabilities: GLCapabilityDriver):
        self.capabilities = capabilities

    def set_depth_test(self, enabled: bool):
        self.capabilities.set_enabled(GLPipelineCapability.DEPTH_TEST, enabled)

    @staticmethod
    def get_depth_write_enabled() -> bool:
        return bool(glGetBooleanv(GL_DEPTH_WRITEMASK))

    @staticmethod
    def set_depth_write(enabled: bool):
        glDepthMask(bool(enabled))

    @staticmethod
    def set_depth_func_gl_less() -> Any:
        return glDepthFunc(GL_LESS)
