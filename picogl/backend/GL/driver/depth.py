from typing import Any

from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_DEPTH_TEST,
    GL_LESS,
    glDepthFunc,
    glDepthMask,
)

from picogl.backend.GL.driver.capability import GLCapabilityDriver


class GLDepthDriver:
    """Depth test, write mask, and depth-function operations."""

    def __init__(self, capabilities: GLCapabilityDriver):
        self.capabilities = capabilities

    def set_depth_test(self, enabled: bool):
        self.capabilities.set_enabled(GL_DEPTH_TEST, enabled)

    @staticmethod
    def set_depth_write(enabled: bool):
        glDepthMask(bool(enabled))

    @staticmethod
    def set_depth_func_gl_less() -> Any:
        return glDepthFunc(GL_LESS)
