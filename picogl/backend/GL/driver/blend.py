"""
GL Blend Driver
"""

from typing import TYPE_CHECKING

from OpenGL.GL import glBlendFunc, glGetIntegerv

from picogl.backend.GL.driver.capability import GLCapabilityDriver
from picogl.backend.capability import GLBlendTarget, GLBlendFactor, GLPipelineCapability
from picogl.backend.state import gl_value

if TYPE_CHECKING:
    from picogl.backend.state import BlendState


class GLBlendDriver:
    """
    GLBlendDriver
    """

    def __init__(self, capabilities: GLCapabilityDriver):
        self.capabilities = capabilities
        self._current: "BlendState | None" = None

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

    def apply(self, state: "BlendState") -> None:
        """Apply a BlendState descriptor, skipping GL when unchanged."""
        if self._current == state:
            return

        prev = self._current
        self._current = state

        if prev is None or prev.enabled != state.enabled:
            self.set_blend(state.enabled)

        if state.enabled and (
            prev is None or prev.src != state.src or prev.dst != state.dst
        ):
            self.set_blend_func(state.src, state.dst)
