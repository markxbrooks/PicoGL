"""
This module provides an OpenGL backend implementation for rendering, state
management, texture handling, and other graphics-related operations. It wraps
OpenGL functionality with a higher-level interface for easier usage in 3D
graphics applications.

Classes:
    - GLBackend: Encapsulates functions for managing OpenGL state and
      performing rendering operations.
"""

from picogl.backend.GL.driver.blend import GLBlendDriver
from picogl.backend.GL.driver.capability import GLCapabilityDriver
from picogl.backend.GL.driver.depth import GLDepthDriver
from picogl.backend.GL.driver.frame import GLFrameDriver
from picogl.backend.GL.driver.geometry import GLGeometryDriver
from picogl.backend.GL.driver.raster import GLRasterDriver
from picogl.backend.GL.driver.texture import GLTextureSystem
from picogl.backend.legacy.core.attribute_binder import LegacyAttributeBinder
from picogl.backend.legacy.core.pipeline import GLLegacyPipeline
from picogl.backend.opengl import GLBindingStrategy, GLPipeline
from picogl.backend.state import (
    DrawCommand,
    GLClipPlaneState,
    GLStateManager,
    RenderState,
    RenderStateApplier,
)
from picogl.buffers.glframe import GLFramebuffer
from picogl.renderer.readback import GLReadback


class GLBackend:
    """GL Backend"""

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
        self.legacy = GLLegacyPipeline()
        self.pipeline: GLPipeline = self.legacy
        self.geometry = GLGeometryDriver(binding)
        self.textures = GLTextureSystem()
        self.attributes = LegacyAttributeBinder()
        self.state_manager = GLStateManager(self.capabilities)
        self.state_applier = RenderStateApplier(self)


    def viewport_old(self, x, y, width, height):
        self.frame.viewport(x, y, width, height)

    def apply_state(self, state: RenderState):
        """Apply a structured render state through this backend."""
        self.state_applier.apply(state)

    def apply_clip_state(self, clip: GLClipPlaneState | None = None):
        """Apply declarative clipping state through the capability subsystem."""
        if clip is not None:
            self.clip = clip
        self.clip.apply(self.state_manager)

    def draw_command(self, command: DrawCommand):
        """Apply command state/resources and draw through this backend."""
        command.execute(self)

    def enable_multisample_old(self):
        self.capabilities.enable_multisample()

    def draw_elements_old(self, mode, indices):
        """draw elements"""
        self.geometry.draw_elements(mode, indices)

    def draw_bound_elements_old(
        self, mode, index_count: int, index_type=None, pointer=None
    ):
        """Draw using the currently bound element buffer."""
        if index_type is None:
            self.geometry.draw_bound_elements(mode, index_count, pointer=pointer)
        else:
            self.geometry.draw_bound_elements(mode, index_count, index_type, pointer)

    def draw_arrays_old(self, mode, first: int, count: int):
        """Draw non-indexed vertex arrays."""
        self.geometry.draw_arrays(mode, first, count)

    def draw_arrays_bound_vao_old(self, vao: int, mode, first: int, count: int):
        """Borrow a VAO handle for a non-indexed draw, then unbind it."""
        self.geometry.draw_arrays_bound_vao(vao, mode, first, count)
