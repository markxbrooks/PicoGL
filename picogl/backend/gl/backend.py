"""
This module provides an OpenGL backend implementation for rendering, state
management, texture handling, and other graphics-related operations. It wraps
OpenGL functionality with a higher-level interface for easier usage in 3D
graphics applications.

Classes:Ï
    - GLBackend: Encapsulates functions for managing OpenGL state and
      performing rendering operations.
"""

import warnings

from picogl.backend.gl.driver.blend import GLBlendDriver
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.driver.depth import GLDepthDriver
from picogl.backend.gl.driver.frame import GLFrameDriver
from picogl.backend.gl.driver.geometry import GLGeometryDriver
from picogl.backend.gl.driver.raster import GLRasterDriver
from picogl.backend.gl.driver.texture import GLTextureSystem
from picogl.backend.legacy.core.attribute_binder import LegacyAttributeBinder
from picogl.backend.legacy.core.pipeline import (GLLegacyPipeline,
                                                 LegacyPipeline)
from picogl.backend.modern.core.pipeline import ShaderPipeline
from picogl.backend.opengl import GLBindingStrategy
from picogl.backend.state import (DrawCommand, GLClipPlaneState,
                                  GLStateManager, RenderState,
                                  RenderStateApplier)
from picogl.gpu.buffers.glframe import GLFramebuffer
from picogl.renderer.readback import GLReadback


class GLBackend:
    """gl Backend"""

    def __init__(self, binding: GLBindingStrategy):
        self.binding = binding
        self.framebuffer = GLFramebuffer()
        self.read = GLReadback()
        self.clip = GLClipPlaneState(enabled0=False, enabled1=False)
        self.capabilities = GLCapabilityDriver()
        self.frame = GLFrameDriver()
        self.depth = GLDepthDriver(self.capabilities)
        self.blend = GLBlendDriver(self.capabilities)
        self.raster = GLRasterDriver()
        self.legacy: LegacyPipeline = GLLegacyPipeline()
        self.shader = ShaderPipeline()
        self.geometry = GLGeometryDriver(binding)
        self.textures = GLTextureSystem()
        self.attributes = LegacyAttributeBinder()
        self.state_manager = GLStateManager(self.capabilities)
        self.state_applier = RenderStateApplier(self)

    @property
    def pipeline(self) -> LegacyPipeline:
        """Deprecated alias for :attr:`legacy`."""
        warnings.warn(
            "GLBackend.pipeline is deprecated; use GLBackend.legacy",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.legacy

    @pipeline.setter
    def pipeline(self, value: LegacyPipeline) -> None:
        warnings.warn(
            "GLBackend.pipeline is deprecated; use GLBackend.legacy",
            DeprecationWarning,
            stacklevel=2,
        )
        self.legacy = value

    def draw_command(self, command: DrawCommand):
        """Apply command state/resources and draw through this backend."""
        command.execute(self)

    def apply_state(self, state: RenderState) -> None:
        """Apply a render-state descriptor through cached subsystem drivers."""
        self.state_applier.apply(state)

    def apply_clip_state(self, clip: GLClipPlaneState | None = None) -> None:
        """Apply clip-plane capability state."""
        if clip is not None:
            self.clip = clip
        self.clip.apply(self.state_manager)

    def create_shader_pipeline(self, program) -> ShaderPipeline:
        """Return a shader pipeline bound to *program*."""
        pipeline = ShaderPipeline(program)
        self.shader = pipeline
        return pipeline
