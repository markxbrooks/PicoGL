from typing import Any

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_BLEND, glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA

from picogl.backend.GL.driver.capability import GLCapabilityDriver
from picogl.backend.state import gl_value


class GLBlendDriver:
    """Blend capability and blend-function operations."""

    def __init__(self, capabilities: GLCapabilityDriver):
        self.capabilities = capabilities

    def set_blend(self, enabled: bool):
        self.capabilities.set_enabled(GL_BLEND, enabled)

    @staticmethod
    def set_blend_func(src: Any, dst: Any) -> None:
        glBlendFunc(gl_value(src), gl_value(dst))

    def setup_blending(self):
        self.set_blend_func(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
