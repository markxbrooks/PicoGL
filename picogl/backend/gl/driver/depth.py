"""
GL Depth Driver
"""

from typing import TYPE_CHECKING, Any

from OpenGL.GL import (GL_DEPTH_WRITEMASK, glDepthFunc, glDepthMask,
                       glGetBooleanv)

from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.gl.driver.applicable_state import ApplicableState
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.glfunc import GLDepthFunc

if TYPE_CHECKING:
    from picogl.backend.state import DepthState


class GLDepthDriver(ApplicableState):
    """Depth test, write mask, and depth-function operations."""

    def __init__(self, capabilities: GLCapabilityDriver):
        super().__init__()
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
        return glDepthFunc(GLDepthFunc.LESS)

    def _do_apply(self, state: "DepthState", prev: "DepthState | None"):
        if prev is None or prev.test != state.test:
            self.set_depth_test(state.test)

        if prev is None or prev.write != state.write:
            self.set_depth_write(state.write)

    def _is_same(self, prev: "DepthState", state: "DepthState"):
        if prev == state:
            return True
        return False
