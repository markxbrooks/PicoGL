from typing import TYPE_CHECKING, Any

from OpenGL.GL import (
    GL_LESS,
    glDepthFunc,
    glDepthMask,
    glGetBooleanv,
    GL_DEPTH_WRITEMASK,
)

from picogl.backend.GL.driver.capability import GLCapabilityDriver
from picogl.backend.capability import GLPipelineCapability

if TYPE_CHECKING:
    from picogl.backend.state import DepthState


class GLDepthDriver:
    """Depth test, write mask, and depth-function operations."""

    def __init__(self, capabilities: GLCapabilityDriver):
        self.capabilities = capabilities
        self._current: "DepthState | None" = None

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

    def apply(self, state: "DepthState") -> None:
        """Apply a DepthState descriptor, skipping GL when unchanged."""
        if self._current == state:
            return

        prev = self._current
        self._current = state

        if prev is None or prev.test != state.test:
            self.set_depth_test(state.test)

        if prev is None or prev.write != state.write:
            self.set_depth_write(state.write)
