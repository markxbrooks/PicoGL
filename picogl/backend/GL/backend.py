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

from OpenGL.GL import (glColorPointer, glDeleteTextures, glDrawElements,
                       glNormalPointer, glTexCoordPointer, glVertexPointer, GL_BLEND, GL_CULL_FACE, GL_VERTEX_ARRAY, GL_FLOAT, GL_UNSIGNED_INT,
                                          GL_DEPTH_TEST, GL_LIGHTING, GL_TEXTURE_2D,
                                          glBlendFunc, glClear, glClearColor,
                                          glColor4f, glDepthMask, glDisable,
                                          glEnable, glIsEnabled, glLightfv,
                                          glLineWidth, glMaterialf,
                                          glMaterialfv, glPolygonMode,
                                          glTexCoord2f, glLoadIdentity,
                                          glVertex3f, glViewport, glMatrixMode, GL_MODELVIEW, GL_COLOR_ARRAY, GL_NORMAL_ARRAY,
                                          GL_TEXTURE_COORD_ARRAY, GL_MULTISAMPLE, GL_CLIP_DISTANCE0, GL_CLIP_DISTANCE1,
                                          GL_FRONT_AND_BACK, GL_LIGHT0,
                                          GL_POSITION, glBindTexture,
                                          glEnableClientState, glTranslatef)
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_COLOR_BUFFER_BIT,
                                          GL_DEPTH_BUFFER_BIT, GL_PROJECTION,
                                          GL_AMBIENT, GL_DIFFUSE, GL_LESS,
                                          GL_SHININESS, GL_SPECULAR,
                                          glDepthFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_CLIP_PLANE0, GL_CLIP_PLANE1
from OpenGL.raw.GLU import gluPerspective

from picogl.backend.capability import FACE_MAP
from picogl.backend.opengl import GLBindingStrategy
from picogl.backend.state import DrawCommand, RenderState, RenderStateApplier, gl_value, GLClipPlaneState
from picogl.buffers.glframe import GLFramebuffer
from picogl.renderer.readback import GLReadback
from picogl.state.texture import TexCoord2f
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


class GLLegacyPipeline:
    """Fixed-function matrix, light, and material operations."""

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


def set_vertex_pointer(data):
    glVertexPointer(3, GL_FLOAT, 0, data)


class GLBackend:
    """GL Backend"""

    def __init__(self, binding: GLBindingStrategy):
        self.binding = binding
        self.framebuffer = GLFramebuffer()
        self.read = GLReadback()
        self.clip = GLClipPlaneState(enabled0=False, enabled1=False)
        self.raster = GLRasterDriver()
        self.legacy = GLLegacyPipeline()
        self.state_applier = RenderStateApplier(self)

    def enable(self, cap):
        glEnable(gl_value(cap))

    def disable(self, cap):
        glDisable(gl_value(cap))

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

    @staticmethod
    def setup_blending():
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    @staticmethod
    def set_depth_write(enabled: bool):
        glDepthMask(bool(enabled))

    @staticmethod
    def set_matrix_mode_model_view():
        glMatrixMode(GL_MODELVIEW)  # Legacy pipeline

    @staticmethod
    def set_matrix_mode_projection():
        glMatrixMode(GL_PROJECTION)

    @staticmethod
    def set_depth_func_gl_less() -> Any:
        return glDepthFunc(GL_LESS)

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

    @staticmethod
    def load_identity():
        glLoadIdentity()  # Reset modelview matrix

    @staticmethod
    def viewport(x, y, width, height):
        glViewport(x, y, width, height)

    @staticmethod
    def set_perspective(fovy, aspect, znear, zfar):
        """Apply a GLU perspective projection to the current matrix."""
        gluPerspective(float(fovy), float(aspect), float(znear), float(zfar))

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

    def set_line_width(self, width):
        self.raster.set_line_width(width)

    @staticmethod
    def set_color(rgba):
        glColor4f(*rgba)

    # --- State ---
    @staticmethod
    def set_blend(enabled: bool):
        glEnable(GL_BLEND) if enabled else glDisable(GL_BLEND)

    def setup_blending_funcs(self):
        self.set_blend_func(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    @staticmethod
    def set_depth_test(enabled: bool):
        glEnable(GL_DEPTH_TEST) if enabled else glDisable(GL_DEPTH_TEST)

    def enable_depth_test(self):
        self.set_depth_test(True)

    @staticmethod
    def set_cull_face(enabled: bool):
        glEnable(GL_CULL_FACE) if enabled else glDisable(GL_CULL_FACE)

    def enable_cull_face(self):
        self.set_cull_face(True)

    def set_polygon_mode(self, *args):
        self.raster.set_polygon_mode(*args)

    @staticmethod
    def set_lighting(enabled: bool):
        glEnable(GL_LIGHTING) if enabled else glDisable(GL_LIGHTING)

    def set_uniform_color(self, color, alpha):
        r, g, b = color[:3]
        self.set_color((r, g, b, 1.0 - alpha))

    # --- Unified Draw ---
    def draw_mesh(self, mesh, mode):
        self.binding.bind_mesh(mesh)
        self.binding.draw(mesh, gl_value(mode))

    def apply_state(self, state: RenderState):
        """Apply a structured render state through this backend."""
        self.state_applier.apply(state)

    def draw_command(self, command: DrawCommand):
        """Apply command state/resources and draw through this backend."""
        command.execute(self)

    @staticmethod
    def enable_multisample():
        glEnable(GL_MULTISAMPLE)

    def enable_clip0(self):
        self.enable(GL_CLIP_DISTANCE0)

    def enable_clip1(self):
        self.enable(GL_CLIP_DISTANCE1)

    def set_clip_plane_enabled(self, plane, enabled: bool):
        """Enable or disable a legacy clipping plane."""
        self.enable(plane) if enabled else self.disable(plane)

    def enable_clip_plane0(self):
        self.set_clip_plane_enabled(GL_CLIP_PLANE0, True)

    def disable_clip_plane0(self):
        self.set_clip_plane_enabled(GL_CLIP_PLANE0, False)

    def enable_clip_plane1(self):
        self.set_clip_plane_enabled(GL_CLIP_PLANE1, True)

    def disable_clip_plane1(self):
        self.set_clip_plane_enabled(GL_CLIP_PLANE1, False)

    @staticmethod
    def enable_vertex_array():
        glEnableClientState(GL_VERTEX_ARRAY)

    @staticmethod
    def enable_normal_array():
        glEnableClientState(GL_NORMAL_ARRAY)

    @staticmethod
    def set_normal_pointer(data):
        glNormalPointer(GL_FLOAT, 0, data)

    @staticmethod
    def enable_color_array():
        glEnableClientState(GL_COLOR_ARRAY)

    @staticmethod
    def set_color_pointer(data, size):
        glColorPointer(size, GL_FLOAT, 0, data)

    @staticmethod
    def enable_texcoord_array():
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    @staticmethod
    def set_texcoord_pointer(data):
        """set texcoord pointer"""
        glTexCoordPointer(2, GL_FLOAT, 0, data)

    @staticmethod
    def draw_elements(mode, indices):
        """draw elements"""
        glDrawElements(mode, len(indices), GL_UNSIGNED_INT, indices)

    @staticmethod
    def bind_texture(texture_id):
        """bind texture"""
        glBindTexture(GL_TEXTURE_2D, texture_id)

    @staticmethod
    def tex_coord2f(coord: TexCoord2f):
        return glTexCoord2f(coord.u, coord.v)

    @staticmethod
    def tex_coords(t1):
        glTexCoord2f(t1[0], t1[1])

    @staticmethod
    def vertex_3f(v1):
        glVertex3f(v1[0], v1[1], v1[2])

    @staticmethod
    def is_enabled(cap):
        """is enabled"""
        return bool(glIsEnabled(gl_value(cap)))

    @staticmethod
    def set_blend_func(src: Any, dst: Any) -> None:
        """set blend function"""
        glBlendFunc(gl_value(src), gl_value(dst))

    @staticmethod
    def create_texture(width, height, data) -> int:
        """create texture"""
        spec = TextureSpec(width=width, height=height)
        tex = Texture2D(spec, data)
        driver = GLTextureDriver()
        driver.create(tex)
        driver.bind(tex)
        driver.initialize(tex)
        return tex.handle

    @staticmethod
    def delete_texture(tex_id: int):
        glDeleteTextures([tex_id])
