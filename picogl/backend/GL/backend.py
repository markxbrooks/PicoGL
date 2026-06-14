"""
This module provides an OpenGL backend implementation for rendering, state
management, texture handling, and other graphics-related operations. It wraps
OpenGL functionality with a higher-level interface for easier usage in 3D
graphics applications.

Classes:
    - GLBackend: Encapsulates functions for managing OpenGL state and
      performing rendering operations.
"""
from OpenGL.GL import (glColorPointer, glDeleteTextures, glDrawElements,
                       glNormalPointer, glTexCoordPointer, glVertexPointer)
from OpenGL.raw.GL._types import GL_FLOAT, GL_UNSIGNED_INT
from OpenGL.raw.GL.ARB.internalformat_query2 import GL_TEXTURE_2D
from OpenGL.raw.GL.KHR.debug import GL_VERTEX_ARRAY
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_BLEND, GL_CULL_FACE,
                                          GL_DEPTH_TEST, GL_LIGHTING,
                                          glBlendFunc, glClear, glClearColor,
                                          glColor4f, glDepthMask, glDisable,
                                          glEnable, glIsEnabled, glLineWidth,
                                          glPolygonMode, glTexCoord2f,
                                          glVertex3f, glViewport)
from OpenGL.raw.GL.VERSION.GL_1_1 import (GL_COLOR_ARRAY, GL_NORMAL_ARRAY,
                                          GL_TEXTURE_COORD_ARRAY,
                                          glBindTexture, glEnableClientState)
from OpenGL.raw.GL.VERSION.GL_1_3 import GL_MULTISAMPLE
from OpenGL.raw.GL.VERSION.GL_3_0 import GL_CLIP_DISTANCE0, GL_CLIP_DISTANCE1
from picogl.backend.opengl import GLBindingStrategy
from picogl.buffers.glframe import GLFramebuffer
from picogl.renderer.readback import GLReadback
from picogl.state.texture import TexCoord2f
from picogl.texture.gltexture import GLTextureDriver, Texture2D, TextureSpec


class GLBackend:
    """GL Backend"""

    def __init__(self, binding: GLBindingStrategy):
        self.binding = binding
        self.framebuffer = GLFramebuffer()
        self.read = GLReadback()

    def enable(self, cap):
        glEnable(cap)

    def disable(self, cap):
        glDisable(cap)

    def clear(self, cap):
        glClear(cap)

    def viewport(self, x, y, width, height):
        glViewport(x, y, width, height)

    def clear_background(self):
        self.framebuffer.clear_background()

    def set_line_width(self, width):
        glLineWidth(width)

    def set_color(self, rgba):
        glColor4f(*rgba)

    # --- State ---
    def set_blend(self, enabled: bool):
        glEnable(GL_BLEND) if enabled else glDisable(GL_BLEND)

    def set_depth_test(self, enabled: bool):
        glEnable(GL_DEPTH_TEST) if enabled else glDisable(GL_DEPTH_TEST)

    def set_depth_write(self, enabled: bool):
        glDepthMask(bool(enabled))

    def set_cull_face(self, enabled: bool):
        glEnable(GL_CULL_FACE) if enabled else glDisable(GL_CULL_FACE)

    def set_polygon_mode(self, face, mode):
        glPolygonMode(face, mode)

    def set_lighting(self, enabled: bool):
        glEnable(GL_LIGHTING) if enabled else glDisable(GL_LIGHTING)

    def set_uniform_color(self, color, alpha):
        r, g, b = color[:3]
        self.set_color((r, g, b, 1.0 - alpha))

    # --- Unified Draw ---
    def draw_mesh(self, mesh, mode):
        self.binding.bind_mesh(mesh)
        self.binding.draw(mesh, mode)

    def enable_multisample(self):
        glEnable(GL_MULTISAMPLE)

    def enable_clip0(self):
        self.enable(GL_CLIP_DISTANCE0)

    def enable_clip1(self):
        self.enable(GL_CLIP_DISTANCE1)

    def clear_color(self, clear_color):
        glClearColor(*clear_color)

    def enable_vertex_array(self):
        glEnableClientState(GL_VERTEX_ARRAY)

    def set_vertex_pointer(self, data):
        glVertexPointer(3, GL_FLOAT, 0, data)

    def enable_normal_array(self):
        glEnableClientState(GL_NORMAL_ARRAY)

    def set_normal_pointer(self, data):
        glNormalPointer(GL_FLOAT, 0, data)

    def enable_color_array(self):
        glEnableClientState(GL_COLOR_ARRAY)

    def set_color_pointer(self, data, size):
        glColorPointer(size, GL_FLOAT, 0, data)

    def enable_texcoord_array(self):
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    def set_texcoord_pointer(self, data):
        """set texcoord pointer"""
        glTexCoordPointer(2, GL_FLOAT, 0, data)

    def draw_elements(self, mode, indices):
        """draw elements"""
        glDrawElements(mode, len(indices), GL_UNSIGNED_INT, indices)

    def bind_texture(self, texture_id):
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

    def is_enabled(self, cap):
        """is enabled"""
        return bool(glIsEnabled(cap))

    def set_blend_func(self, src, dst):
        """set blend function"""
        glBlendFunc(src, dst)

    def create_texture(self, width, height, data) -> int:
        """create texture"""
        spec = TextureSpec(width=width, height=height)
        tex = Texture2D(spec, data)
        driver = GLTextureDriver()
        driver.create(tex)
        driver.bind(tex)
        driver.initialize(tex)
        return tex.handle

    def delete_texture(self, tex_id: int):
        glDeleteTextures([tex_id])