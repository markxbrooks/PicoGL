"""
This module provides an OpenGL backend implementation for rendering, state
management, texture handling, and other graphics-related operations. It wraps
OpenGL functionality with a higher-level interface for easier usage in 3D
graphics applications.

Classes:
    - GLBackend: Encapsulates functions for managing OpenGL state and
      performing rendering operations.
"""

from typing import Any

from OpenGL.GL import (
    GL_BLEND_DST,
    GL_BLEND_SRC,
    GL_DEPTH_WRITEMASK,
    GL_LINE_WIDTH,
    GL_POLYGON_MODE,
    glClear,
    glClearColor,
    glGetBooleanv,
    glGetFloatv,
    glGetIntegerv,
    glViewport,
)

from picogl.backend.GL.driver.blend import GLBlendDriver
from picogl.backend.GL.driver.capability import GLCapabilityDriver
from picogl.backend.GL.driver.depth import GLDepthDriver
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
    gl_value,
)
from picogl.buffers.glframe import GLFramebuffer
from picogl.renderer.readback import GLReadback
from picogl.state.draw_mode import GLBitMask
from picogl.state.fill import GLColorMaterialMode, GLFace, GLLight
from picogl.state.texture import TexCoord2f


class GLBackend:
    """GL Backend"""

    def __init__(self, binding: GLBindingStrategy):
        self.binding = binding
        self.framebuffer = GLFramebuffer()
        self.read = GLReadback()
        self.clip = GLClipPlaneState(enabled0=False, enabled1=False)
        self.capabilities = GLCapabilityDriver()
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

    def enable(self, cap):
        self.capabilities.enable(cap)

    def disable(self, cap):
        self.capabilities.disable(cap)

    def clear(self, cap):
        glClear(gl_value(cap))

    def set_clear_color(self, color=(0.0, 0.0, 0.0, 1.0)):
        """Set the OpenGL clear color without clearing the framebuffer."""
        glClearColor(*color)

    def set_clear_background_and_color(self, color=(0.0, 0.0, 0.0, 1.0)):
        """
        Clears the screen to a specified color using OpenGL commands.

        This method sets the clear color and then clears the color buffer
        to ensure the screen is rendered with the specified or default background
        color.

        Args:
            color (tuple[float, float, float, float]): A tuple representing the RGBA
                color values to clear the screen. Each value should be between
                0.0 and 1.0. Defaults to (0.0, 0.0, 0.0, 1.0).
        """
        self.set_clear_color(color)
        self.clear_background()

    def set_depth_write_old(self, enabled: bool):
        self.depth.set_depth_write(enabled)

    @staticmethod
    def get_depth_write_enabled() -> bool:
        return bool(glGetBooleanv(GL_DEPTH_WRITEMASK))

    def set_matrix_mode_model_view_old(self):
        self.pipeline.set_matrix_mode_model_view()

    def set_matrix_mode_projection(self):
        self.pipeline.set_matrix_mode_projection()

    def set_depth_func_gl_less(self) -> Any:
        return self.depth.set_depth_func_gl_less()

    def clear_background(self):
        """
        Clears the background by removing all color and depth information from
        the current OpenGL framebuffer.

        This method clears the framebuffer's color and depth buffers, preparing
        it for rendering the next frame.

        Raises:
            OpenGL.GL.error.GLError: If an OpenGL error occurs during the
            clearing operation.
        """
        self.clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)

    def load_identity(self):
        self.pipeline.load_identity()

    @staticmethod
    def viewport(x, y, width, height):
        glViewport(x, y, width, height)

    def set_perspective_old(self, fovy, aspect, znear, zfar):
        """Apply a GLU perspective projection to the current matrix."""
        self.pipeline.set_perspective(fovy, aspect, znear, zfar)

    # -- Legacy ---

    def translate_old(self, x, y, z):
        """Apply a legacy fixed-function translation."""
        self.legacy.translate(x, y, z)

    def set_light_position_old(self, position, light: GLLight=GLLight.LIGHT0):
        """Set a fixed-function light position."""
        self.legacy.set_light(position, light=light)

    def set_material_old(self, face: GLFace, material: GLColorMaterialMode):
        """Set fixed-function Phong material values."""
        self.legacy.set_material(face, material)

    def set_color_material_old(
        self,
        face=GLFace.FRONT_AND_BACK,
        mode=GLColorMaterialMode.AMBIENT_AND_DIFFUSE,
    ):
        """Set fixed-function color material tracking."""
        self.legacy.set_color_material(face, mode)

    def set_line_width_old(self, width: int):
        self.raster.set_line_width(width)

    def set_point_size_old(self, size: int):
        self.raster.set_point_size(size)

    def set_clamped_point_size_old(self, size: int):
        self.raster.set_clamped_point_size(size)

    def set_polygon_offset_old(self, factor, units):
        self.raster.set_polygon_offset(factor, units)

    def set_color_old(self, rgba):
        self.pipeline.set_color(rgba)

    # --- State ---
    def set_capability_enabled_old(self, cap, enabled: bool):
        self.capabilities.set_enabled(cap, enabled)

    def set_polygon_mode_old(self, *args):
        self.raster.set_polygon_mode(*args)

    @staticmethod
    def get_polygon_mode_old():
        return glGetIntegerv(GL_POLYGON_MODE)

    @staticmethod
    def get_line_width_old() -> float:
        return float(glGetFloatv(GL_LINE_WIDTH))

    # --- Unified Draw ---
    def draw_mesh_old(self, mesh, mode):
        self.geometry.draw_mesh(mesh, mode)

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

    def enable_multisample(self):
        self.capabilities.enable_multisample()

    def draw_elements(self, mode, indices):
        """draw elements"""
        self.geometry.draw_elements(mode, indices)

    def draw_bound_elements(
        self, mode, index_count: int, index_type=None, pointer=None
    ):
        """Draw using the currently bound element buffer."""
        if index_type is None:
            self.geometry.draw_bound_elements(mode, index_count, pointer=pointer)
        else:
            self.geometry.draw_bound_elements(mode, index_count, index_type, pointer)

    def draw_arrays(self, mode, first: int, count: int):
        """Draw non-indexed vertex arrays."""
        self.geometry.draw_arrays(mode, first, count)

    def draw_arrays_bound_vao(self, vao: int, mode, first: int, count: int):
        """Borrow a VAO handle for a non-indexed draw, then unbind it."""
        self.geometry.draw_arrays_bound_vao(vao, mode, first, count)

    def bind_texture(self, texture_id):
        """bind texture"""
        self.textures.bind_texture(texture_id)

    def tex_coord2f(self, coord: TexCoord2f):
        return self.pipeline.tex_coord2f(coord)

    def vertex_3f_old(self, v1):
        self.pipeline.vertex_3f(v1)

    def is_enabled_old(self, cap):
        """is enabled"""
        return self.capabilities.is_enabled(cap)

    @staticmethod
    def get_blend_func() -> tuple[int, int]:
        return int(glGetIntegerv(GL_BLEND_SRC)), int(glGetIntegerv(GL_BLEND_DST))

    def create_texture(self, width, height, data) -> int:
        """create texture"""
        return self.textures.create_texture(width, height, data)

    def delete_texture(self, tex_id: int):
        self.textures.delete_texture(tex_id)
