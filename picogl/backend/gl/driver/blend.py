"""
A driver for managing OpenGL blending functionality.

This module provides a driver class for configuring and applying blending
settings using OpenGL. It interacts with low-level OpenGL capabilities
and provides methods for enabling blending, setting blending functions,
and updating blending states. The driver works in conjunction with the
capability driver and state objects to manage blending-related operations
efficiently.
"""

from typing import TYPE_CHECKING

from backend.gl.wrappers import gl_get_integerv
from backend.gl.wrappers.blending import gl_blend_func
from picogl.backend.gl.capability import (
    GLBlendFactor,
    GLBlendTarget,
    GLPipelineCapability,
)
from picogl.backend.gl.driver.applyable import Applyable
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.state import gl_value

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
    def set_blend_func(src: GLBlendFactor | int, dst: GLBlendFactor | int):
        gl_blend_func(int(gl_value(src)), int(gl_value(dst)))

    @staticmethod
    def get_blend_func() -> tuple[GLBlendFactor, GLBlendFactor]:
        c = GLCapabilityDriver
        src = GLBlendFactor.from_gl(int(gl_get_integerv(GLBlendTarget.BLEND_SRC)))
        dst = GLBlendFactor.from_gl(int(gl_get_integerv(GLBlendTarget.BLEND_DST)))
        return src, dst

    def set_alpha_blending(self):
        self.set_blend_func(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)

    def _do_apply(self, state: "BlendState | None", prev: "BlendState | None"):
        if state is None:
            return
        if prev is None or prev.enabled != state.enabled:
            self.set_blend(state.enabled)

        if state.enabled and (
            prev is None or prev.src != state.src or prev.dst != state.dst
        ):
            self.set_blend_func(state.src, state.dst)

    def _is_same(self, prev: "BlendState", state: "BlendState") -> bool:
        return prev == state
