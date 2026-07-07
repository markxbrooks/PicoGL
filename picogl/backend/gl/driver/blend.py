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

from picogl.backend.gl.wrappers import gl_get_integerv
from picogl.backend.gl.wrappers.blending import gl_blend_func
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
        """
        Sets the blending capability for the pipeline.

        This method updates the blending state of the pipeline by enabling or disabling
        the blending functionality, which determines how pixels are blended together
        when rendered.

        Parameters:
            enabled (bool): Specifies whether the blending capability should be enabled
            (True) or disabled (False).
        """
        self.capabilities.set_enabled(GLPipelineCapability.BLEND, enabled)

    @staticmethod
    def set_blend_func(src: GLBlendFactor | int, dst: GLBlendFactor | int):
        """
        Sets the blending function for OpenGL rendering.

        This method specifies how the colors of a source and destination are combined
        to produce a final color in OpenGL. The blending function is defined by the
        source and destination blend factors. These factors determine the influence
        of the source (incoming) and destination (existing framebuffer) pixel values
        during blending.

        Parameters:
            src (GLBlendFactor | int): The source blending factor. This determines how
                the incoming pixel color contributes to the final blended color.
            dst (GLBlendFactor | int): The destination blending factor. This determines
                how the existing framebuffer pixel color contributes to the final
                blended color.

        Returns:
            None
        """
        gl_blend_func(int(gl_value(src)), int(gl_value(dst)))

    @staticmethod
    def get_blend_func() -> tuple[GLBlendFactor, GLBlendFactor]:
        """
        Retrieves the current OpenGL blend function factors for the source and destination.

        Returns
        -------
        tuple[GLBlendFactor, GLBlendFactor]
            A tuple containing the source and destination blend factors as
            GLBlendFactor instances.
        """
        c = GLCapabilityDriver
        src = GLBlendFactor.from_gl(int(gl_get_integerv(GLBlendTarget.BLEND_SRC)))
        dst = GLBlendFactor.from_gl(int(gl_get_integerv(GLBlendTarget.BLEND_DST)))
        return src, dst

    def set_alpha_blending(self):
        """
        Sets the alpha blending mode for rendering.

        Alpha blending is configured by specifying source and destination
        blend functions. This method sets the blend function to use the
        source alpha channel and the inverse of the source alpha channel
        for blending.

        Raises:
            Any exceptions raised by set_blend_func method will be propagated.
        """
        self.set_blend_func(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)

    def _do_apply(self, state: "BlendState | None", prev: "BlendState | None"):
        """
        Performs the application of a new blending state to the current render state.

        This method compares the provided blending state with the previous state and applies
        necessary changes based on the differences. If no new blending state is specified, the
        method exits without making any changes.

        Parameters:
            state (BlendState | None): The new blending state to apply. If None, no changes
                will be made to the current state.
            prev (BlendState | None): The previous blending state. Used to determine which
                properties have changed and need to be applied to the current state.
        """
        if state is None:
            return
        if prev is None or prev.enabled != state.enabled:
            self.set_blend(state.enabled)

        if state.enabled and (
            prev is None or prev.src != state.src or prev.dst != state.dst
        ):
            self.set_blend_func(state.src, state.dst)

    def _is_same(self, prev: "BlendState", state: "BlendState") -> bool:
        """
        Determines if two BlendState instances are equal.

        This function compares two BlendState objects and returns a boolean
        indicating if they are equivalent.

        Parameters:
        prev : BlendState
            The first BlendState object to compare.
        state : BlendState
            The second BlendState object to compare.

        Returns:
        bool
            True if the two BlendState objects are equal, otherwise False.
        """
        return prev == state
