"""
GL Blend Driver
"""

from typing import TYPE_CHECKING

from OpenGL.GL import glBlendFunc

from picogl.backend.capability import GLBlendFactor, GLBlendTarget, GLPipelineCapability
from picogl.backend.GL.driver.applyable import Applyable
from picogl.backend.GL.driver.capability import GLCapabilityDriver
from picogl.backend.state import BlendState, gl_value

if TYPE_CHECKING:
    from picogl.backend.state import BlendState


class GLBlendDriver(Applyable):
    """
    GLBlendDriver
    """

    def __init__(self, capabilities: GLCapabilityDriver):
        super().__init__()
        self.capabilities = capabilities

    def set_blend(self, enabled: bool):
        self.capabilities.set_enabled(GLPipelineCapability.BLEND, enabled)

    @staticmethod
    def set_blend_func(src: GLBlendFactor, dst: GLBlendFactor):
        glBlendFunc(gl_value(src), gl_value(dst))

    @staticmethod
    def get_blend_func() -> tuple[GLBlendFactor, GLBlendFactor]:
        c = self.capabilities
        src = GLBlendFactor.from_gl(int(c.get_integerv(GLBlendTarget.BLEND_SRC)))
        dst = GLBlendFactor.from_gl(int(c.get_integerv(GLBlendTarget.BLEND_DST)))
        return src, dst

    def setup_blending(self):
        self.set_blend_func(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)

    def _do_apply(self, state: BlendState | None, prev: BlendState | None):
        if state is None:
            return
        if prev is None or prev.enabled != state.enabled:
            self.set_blend(state.enabled)

        if state.enabled and (
            prev is None or prev.src != state.src or prev.dst != state.dst
        ):
            self.set_blend_func(state.src, state.dst)

    def _is_same(self, prev: BlendState, state: BlendState) -> bool:
        if prev == state:
            return True
        return False
