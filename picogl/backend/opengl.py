"""
GL Backend Interface.

This module provides an interface for a GL backend implementation, which
offers functionalities for managing OpenGL state, drawing meshes, managing
materials, handling client-side arrays, and interacting with textures.

Classes:
    GLBackend: A class defining the interface for the GL backend with
               various methods for rendering and managing rendering states.
"""
from abc import ABC, abstractmethod
from typing import Any

from numpy import dtype, generic, ndarray
from OpenGL.GL import (GL_BLEND, GL_CULL_FACE, GL_VERTEX_ARRAY, glTexCoordPointer, glDrawElements,
                       glReadPixels, glEnableClientState,
                        GL_CLIP_DISTANCE0, GL_CLIP_DISTANCE1, glViewport, GL_FLOAT, GL_UNSIGNED_INT, glEnable, glDisable, glClear, \
    glLineWidth, glColor4f, GL_DEPTH_TEST, glDepthMask, glPolygonMode, GL_LIGHTING, glClearColor, GL_TEXTURE_2D, \
    glTexCoord2f, glVertex3f, glIsEnabled, glBlendFunc, glVertexPointer, GL_NORMAL_ARRAY, glNormalPointer, \
    GL_COLOR_ARRAY, glColorPointer, GL_TEXTURE_COORD_ARRAY, glBindTexture, glDeleteTextures, GL_MULTISAMPLE)

from picogl.buffers.glframe import GLFramebuffer
from picogl.texture.gltexture import GLTexture2D
from picogl.state.texture import TexCoord2f


class AbstractGLBackend(ABC):
    """
    ALL rendering must go through this interface.
    """

    @abstractmethod
    def set_blend(self, enabled: bool): ...

    @abstractmethod
    def set_depth_test(self, enabled: bool): ...

    @abstractmethod
    def set_depth_write(self, enabled: bool): ...

    @abstractmethod
    def set_cull_face(self, enabled: bool): ...

    @abstractmethod
    def set_line_width(self, width: float): ...

    @abstractmethod
    def set_polygon_mode(self, mode: int): ...

    @abstractmethod
    def set_lighting(self, enabled: bool): ...

    @abstractmethod
    def set_uniform_color(self, color: tuple, alpha: float): ...

    @abstractmethod
    def draw_elements(self, mode: int, indices): ...


class GLBindingStrategy(ABC):
    @abstractmethod
    def bind_mesh(self, mesh): ...

    @abstractmethod
    def draw(self, mesh, mode): ...


class LegacyBinding(GLBindingStrategy):
    def bind_mesh(self, mesh):
        if mesh.vertices is not None:
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, mesh.vertices)

        if mesh.normals is not None:
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, mesh.normals)

        if mesh.colors is not None:
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(4, GL_FLOAT, 0, mesh.colors)

        if mesh.texcoords is not None:
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glTexCoordPointer(2, GL_FLOAT, 0, mesh.texcoords)

    def draw(self, mesh, mode):
        if mesh.indices is not None:
            glDrawElements(mode, len(mesh.indices), GL_UNSIGNED_INT, mesh.indices)


class ModernBinding(GLBindingStrategy):
    def bind_mesh(self, mesh):
        mesh.vao.bind()   # assumes VAO already configured

    def draw(self, mesh, mode):
        if mesh.ebo is not None:
            glDrawElements(mode, mesh.index_count, GL_UNSIGNED_INT, None)


class GLBackend:
    def __init__(self, binding: GLBindingStrategy):
        self.binding = binding
        self.framebuffer = GLFramebuffer()

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

    def read_pixels(self, depth: ndarray[Any, dtype[Any]] | ndarray[Any, dtype[generic]], x: int, y_gl: int):
        glReadPixels(x, y_gl, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, depth)

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
        texture = GLTexture2D(width=width, height=height)
        texture.bind()
        texture.set_parameters()
        texture.upload(data)
        texture.generate_mipmap()
        return texture.id

    def delete_texture(self, tex_id: int):
        glDeleteTextures([tex_id])


