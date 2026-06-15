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

from OpenGL.GL import (GL_AMBIENT_AND_DIFFUSE, GL_BLEND_DST, GL_BLEND_SRC,
                       GL_DEPTH_WRITEMASK,
                       GL_LINE_WIDTH, GL_POLYGON_MODE, glColorPointer,
                       glDeleteTextures, glDrawElements, glGetBooleanv,
                       glGetFloatv, glGetIntegerv, glNormalPointer,
                       glTexCoordPointer, glVertexPointer, GL_BLEND, GL_CULL_FACE, GL_VERTEX_ARRAY,
                       GL_FLOAT, GL_UNSIGNED_INT,
                       GL_DEPTH_TEST, GL_LIGHTING, GL_TEXTURE_2D,
                       glBlendFunc, glClear, glClearColor,
                       glColor4f, glColorMaterial, glDepthMask, glDisable,
                       glEnable, glIsEnabled, glLightfv,
                       glLineWidth, glMaterialf,
                       glMaterialfv, glPolygonMode,
                       glTexCoord2f, glLoadIdentity,
                       glVertex3f, glViewport, glMatrixMode, GL_MODELVIEW, GL_COLOR_ARRAY, GL_NORMAL_ARRAY,
                       GL_TEXTURE_COORD_ARRAY, GL_MULTISAMPLE, GL_CLIP_DISTANCE0, GL_CLIP_DISTANCE1,
                       GL_FRONT_AND_BACK, GL_LIGHT0,
                       GL_POSITION, glBindTexture,
                       glDisableClientState, glEnableClientState, glTranslatef)
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_COLOR_BUFFER_BIT,
                                          GL_DEPTH_BUFFER_BIT, GL_PROJECTION,
                                          GL_AMBIENT, GL_DIFFUSE, GL_LESS,
                                          GL_SHININESS, GL_SPECULAR,
                                          glDepthFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_CLIP_PLANE0, GL_CLIP_PLANE1
from OpenGL.raw.GLU import gluPerspective

from picogl.backend.capability import FACE_MAP
from picogl.backend.opengl import GLBindingStrategy, GLPipeline
from picogl.backend.state import DrawCommand, RenderState, RenderStateApplier, gl_value, GLClipPlaneState
from picogl.buffers.glframe import GLFramebuffer
from picogl.renderer.readback import GLReadback
from picogl.state.texture import TexCoord2f, Vertex3f
from picogl.texture.gltexture import GLTextureDriver, Texture2D, TextureSpec


class GLRasterDriver:
    """Fixed-function raster state operations."""

    @staticmethod
    def set_line_width(width):
        glLineWidth(width)

    @staticmethod
    def set_polygon_mode(*args):
        if len(args) == 1:
            face, mode = GL_FRONT_AND_BACK, args[0]
        elif len(args) == 2:
            face, mode = args
        else:
            raise TypeError("set_polygon_mode expects mode or face, mode")
        glPolygonMode(gl_value(face), gl_value(mode))


class GLCapabilityDriver:
    """OpenGL capability toggles and queries."""

    @staticmethod
    def enable(cap):
        glEnable(gl_value(cap))

    @staticmethod
    def disable(cap):
        glDisable(gl_value(cap))

    def set_enabled(self, cap, enabled: bool):
        self.enable(cap) if enabled else self.disable(cap)

    @staticmethod
    def is_enabled(cap) -> bool:
        return bool(glIsEnabled(gl_value(cap)))

    def enable_multisample(self):
        self.enable(GL_MULTISAMPLE)

    def set_clip_plane_enabled(self, plane, enabled: bool):
        self.set_enabled(plane, enabled)


class GLDepthDriver:
    """Depth test, write mask, and depth-function operations."""

    def __init__(self, capabilities: GLCapabilityDriver):
        self.capabilities = capabilities

    def set_depth_test(self, enabled: bool):
        self.capabilities.set_enabled(GL_DEPTH_TEST, enabled)

    @staticmethod
    def set_depth_write(enabled: bool):
        glDepthMask(bool(enabled))

    @staticmethod
    def set_depth_func_gl_less() -> Any:
        return glDepthFunc(GL_LESS)


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


class GLLegacyPipeline:
    """Fixed-function matrix, light, and material operations."""

    @staticmethod
    def set_matrix_mode_model_view():
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def set_matrix_mode_projection():
        glMatrixMode(GL_PROJECTION)

    @staticmethod
    def load_identity():
        glLoadIdentity()

    @staticmethod
    def set_perspective(fovy, aspect, znear, zfar):
        gluPerspective(float(fovy), float(aspect), float(znear), float(zfar))

    @staticmethod
    def set_projection(fovy, aspect, znear, zfar):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(float(fovy), float(aspect), float(znear), float(zfar))
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def translate(x, y, z):
        glTranslatef(float(x), float(y), float(z))

    @staticmethod
    def set_light(position, light=GL_LIGHT0):
        glLightfv(gl_value(light), GL_POSITION, position)

    @staticmethod
    def set_material(face, material):
        f = FACE_MAP.get(face, gl_value(face))
        glMaterialfv(f, GL_AMBIENT, material.ambient)
        glMaterialfv(f, GL_DIFFUSE, material.diffuse)
        glMaterialfv(f, GL_SPECULAR, material.specular)
        glMaterialf(f, GL_SHININESS, material.shininess)

    @staticmethod
    def set_color_material(face=GL_FRONT_AND_BACK, mode=GL_AMBIENT_AND_DIFFUSE):
        f = FACE_MAP.get(face, gl_value(face))
        glColorMaterial(f, gl_value(mode))

    @staticmethod
    def set_color(rgba):
        glColor4f(*rgba)

    def set_uniform_color(self, color, alpha):
        r, g, b = color[:3]
        self.set_color((r, g, b, 1.0 - alpha))

    @staticmethod
    def tex_coord2f(coord: TexCoord2f):
        return glTexCoord2f(coord.u, coord.v)

    @staticmethod
    def vertex_3f(v1: Vertex3f):
        glVertex3f(v1.x, v1.y, v1.z)


class GLGeometryDriver:
    """Mesh binding and indexed draw operations."""

    def __init__(self, binding: GLBindingStrategy):
        self.binding = binding

    def draw_mesh(self, mesh, mode):
        self.binding.bind_mesh(mesh)
        self.binding.draw(mesh, gl_value(mode))

    @staticmethod
    def draw_elements(mode, indices):
        glDrawElements(gl_value(mode), len(indices), GL_UNSIGNED_INT, indices)


class GLTextureSystem:
    """Texture creation, binding, and deletion."""

    def __init__(self, driver: GLTextureDriver | None = None):
        self.driver = driver or GLTextureDriver()

    def create_texture(self, width, height, data) -> int:
        spec = TextureSpec(width=width, height=height)
        tex = Texture2D(spec, data)
        self.driver.create(tex)
        self.driver.bind(tex)
        self.driver.initialize(tex)
        return tex.handle

    @staticmethod
    def bind_texture(texture_id):
        glBindTexture(GL_TEXTURE_2D, texture_id)

    @staticmethod
    def delete_texture(tex_id: int):
        glDeleteTextures([tex_id])


class LegacyAttributeBinder:
    """Legacy client-state and vertex attribute pointer operations."""

    @staticmethod
    def enable_vertex_array():
        glEnableClientState(GL_VERTEX_ARRAY)

    @staticmethod
    def disable_vertex_array():
        """disable vertex array"""
        glDisableClientState(GL_VERTEX_ARRAY)

    @staticmethod
    def set_vertex_pointer(data):
        glVertexPointer(3, GL_FLOAT, 0, data)

    @staticmethod
    def enable_normal_array():
        glEnableClientState(GL_NORMAL_ARRAY)

    @staticmethod
    def disable_normal_array():
        glDisableClientState(GL_NORMAL_ARRAY)

    @staticmethod
    def set_normal_pointer(data):
        glNormalPointer(GL_FLOAT, 0, data)

    @staticmethod
    def enable_color_array():
        glEnableClientState(GL_COLOR_ARRAY)

    @staticmethod
    def disable_color_array():
        glDisableClientState(GL_COLOR_ARRAY)

    @staticmethod
    def set_color_pointer(data, size):
        glColorPointer(size, GL_FLOAT, 0, data)

    @staticmethod
    def enable_texcoord_array():
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    @staticmethod
    def disable_texcoord_array():
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    @staticmethod
    def set_texcoord_pointer(data):
        glTexCoordPointer(2, GL_FLOAT, 0, data)


def set_vertex_pointer(data):
    LegacyAttributeBinder.set_vertex_pointer(data)


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
        self.state_applier = RenderStateApplier(self)

    def enable(self, cap):
        self.capabilities.enable(cap)

    def disable(self, cap):
        self.capabilities.disable(cap)

    def clear(self, cap):
        glClear(gl_value(cap))

    def clear_grey(self) -> Any:
        self.set_clear_background_and_color(color=(0.2, 0.2, 0.2, 0.0))

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

    def setup_blending(self):
        self.blend.setup_blending()

    def set_depth_write(self, enabled: bool):
        self.depth.set_depth_write(enabled)

    @staticmethod
    def get_depth_write_enabled() -> bool:
        return bool(glGetBooleanv(GL_DEPTH_WRITEMASK))

    def set_matrix_mode_model_view(self):
        self.pipeline.set_matrix_mode_model_view()

    def set_matrix_mode_projection(self):
        self.pipeline.set_matrix_mode_projection()

    def set_depth_func_gl_less(self) -> Any:
        return self.depth.set_depth_func_gl_less()

    @staticmethod
    def clear_background():
        """
        Clears the background by removing all color and depth information from
        the current OpenGL framebuffer.

        This method clears the framebuffer's color and depth buffers, preparing
        it for rendering the next frame.

        Raises:
            OpenGL.GL.error.GLError: If an OpenGL error occurs during the
            clearing operation.
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def load_identity(self):
        self.pipeline.load_identity()

    @staticmethod
    def viewport(x, y, width, height):
        glViewport(x, y, width, height)

    def set_perspective(self, fovy, aspect, znear, zfar):
        """Apply a GLU perspective projection to the current matrix."""
        self.pipeline.set_perspective(fovy, aspect, znear, zfar)

    # -- Legacy ---

    def set_perspective_projection(self, fovy, aspect, znear, zfar):
        """Configure the legacy projection matrix and return to modelview mode."""
        self.legacy.set_projection(fovy, aspect, znear, zfar)

    def translate(self, x, y, z):
        """Apply a legacy fixed-function translation."""
        self.legacy.translate(x, y, z)

    def set_light_position(self, position, light=GL_LIGHT0):
        """Set a fixed-function light position."""
        self.legacy.set_light(position, light=light)

    def set_material(self, face, material):
        """Set fixed-function Phong material values."""
        self.legacy.set_material(face, material)

    def set_color_material(self, face=GL_FRONT_AND_BACK, mode=GL_AMBIENT_AND_DIFFUSE):
        """Set fixed-function color material tracking."""
        self.legacy.set_color_material(face, mode)

    def set_line_width(self, width):
        self.raster.set_line_width(width)

    def set_color(self, rgba):
        self.pipeline.set_color(rgba)

    # --- State ---
    def set_blend(self, enabled: bool):
        self.blend.set_blend(enabled)

    def setup_blending_funcs(self):
        self.blend.setup_blending()

    def set_depth_test(self, enabled: bool):
        self.depth.set_depth_test(enabled)

    def enable_depth_test(self):
        self.set_depth_test(True)

    def set_cull_face(self, enabled: bool):
        self.capabilities.set_enabled(GL_CULL_FACE, enabled)

    def set_capability_enabled(self, cap, enabled: bool):
        self.capabilities.set_enabled(cap, enabled)

    def enable_cull_face(self):
        self.set_cull_face(True)

    def set_polygon_mode(self, *args):
        self.raster.set_polygon_mode(*args)

    @staticmethod
    def get_polygon_mode():
        return glGetIntegerv(GL_POLYGON_MODE)

    @staticmethod
    def get_line_width() -> float:
        return float(glGetFloatv(GL_LINE_WIDTH))

    def set_lighting(self, enabled: bool):
        self.capabilities.set_enabled(GL_LIGHTING, enabled)

    def set_uniform_color(self, color, alpha):
        self.pipeline.set_uniform_color(color, alpha)

    # --- Unified Draw ---
    def draw_mesh(self, mesh, mode):
        self.geometry.draw_mesh(mesh, mode)

    def apply_state(self, state: RenderState):
        """Apply a structured render state through this backend."""
        self.state_applier.apply(state)

    def draw_command(self, command: DrawCommand):
        """Apply command state/resources and draw through this backend."""
        command.execute(self)

    def enable_multisample(self):
        self.capabilities.enable_multisample()

    def enable_clip0(self):
        self.enable(GL_CLIP_DISTANCE0)

    def enable_clip1(self):
        self.enable(GL_CLIP_DISTANCE1)

    def set_clip_plane_enabled(self, plane, enabled: bool):
        """Enable or disable a legacy clipping plane."""
        self.capabilities.set_clip_plane_enabled(plane, enabled)

    def enable_clip_plane0(self):
        self.set_clip_plane_enabled(GL_CLIP_PLANE0, True)

    def disable_clip_plane0(self):
        self.set_clip_plane_enabled(GL_CLIP_PLANE0, False)

    def enable_clip_plane1(self):
        self.set_clip_plane_enabled(GL_CLIP_PLANE1, True)

    def disable_clip_plane1(self):
        self.set_clip_plane_enabled(GL_CLIP_PLANE1, False)

    def enable_vertex_array(self):
        self.attributes.enable_vertex_array()

    def disable_vertex_array(self):
        self.attributes.disable_vertex_array()

    def set_vertex_pointer(self, data):
        self.attributes.set_vertex_pointer(data)

    def enable_normal_array(self):
        self.attributes.enable_normal_array()

    def disable_normal_array(self):
        self.attributes.disable_normal_array()

    def set_normal_pointer(self, data):
        self.attributes.set_normal_pointer(data)

    def enable_color_array(self):
        self.attributes.enable_color_array()

    def disable_color_array(self):
        self.attributes.disable_color_array()

    def set_color_pointer(self, data, size):
        self.attributes.set_color_pointer(data, size)

    def enable_texcoord_array(self):
        self.attributes.enable_texcoord_array()

    def disable_texcoord_array(self):
        self.attributes.disable_texcoord_array()

    def set_texcoord_pointer(self, data):
        """set texcoord pointer"""
        self.attributes.set_texcoord_pointer(data)

    def draw_elements(self, mode, indices):
        """draw elements"""
        self.geometry.draw_elements(mode, indices)

    def bind_texture(self, texture_id):
        """bind texture"""
        self.textures.bind_texture(texture_id)

    def tex_coord2f(self, coord: TexCoord2f):
        return self.pipeline.tex_coord2f(coord)

    def vertex_3f(self, v1):
        self.pipeline.vertex_3f(v1)

    def is_enabled(self, cap):
        """is enabled"""
        return self.capabilities.is_enabled(cap)

    def set_blend_func(self, src: Any, dst: Any) -> None:
        """set blend function"""
        self.blend.set_blend_func(src, dst)

    @staticmethod
    def get_blend_func() -> tuple[int, int]:
        return int(glGetIntegerv(GL_BLEND_SRC)), int(glGetIntegerv(GL_BLEND_DST))

    def create_texture(self, width, height, data) -> int:
        """create texture"""
        return self.textures.create_texture(width, height, data)

    def delete_texture(self, tex_id: int):
        self.textures.delete_texture(tex_id)
