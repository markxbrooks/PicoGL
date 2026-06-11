from abc import ABC
from enum import Enum

from numpy import dtype, generic, ndarray
from typing import Any

from OpenGL.GL import (GL_CLAMP_TO_EDGE, GL_LINEAR, GL_RGB, GL_TEXTURE_2D,
                       GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER, GL_CLIP_DISTANCE0, GL_CLIP_DISTANCE1,
                       GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_UNSIGNED_BYTE, glReadPixels, glViewport, GL_FILL, GL_LINE,
                       glBindTexture, glDrawElements, glGenTextures, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
                       glTexCoordPointer, glTexImage2D, glTexParameteri, glClearColor, glClear, GL_MULTISAMPLE, GL_DEPTH_COMPONENT)
from OpenGL.GL.framebufferobjects import glGenerateMipmap
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_FLOAT, GL_LINEAR_MIPMAP_LINEAR,
                                          GL_UNSIGNED_INT, glBlendFunc,
                                          glColor4f, glDisable, glEnable,
                                          glIsEnabled, glLineWidth,
                                          glPolygonMode, glTexCoord2f, glVertex3f)
from OpenGL.raw.GL.VERSION.GL_1_1 import (GL_COLOR_ARRAY, GL_NORMAL_ARRAY,
                                          GL_TEXTURE_COORD_ARRAY,
                                          GL_VERTEX_ARRAY, glColorPointer,
                                          glDeleteTextures,
                                          glEnableClientState, glNormalPointer,
                                          glVertexPointer)
from picogl.backend.opengl import GLBackend

from picogl.state.texture import TexCoord2f


class PolygonMode(Enum):
    FILL = GL_FILL
    LINE = GL_LINE


class LegacyGLBackend(GLBackend):
    """Legacy GL Backend"""
    def enable(self, cap):
        glEnable(cap)

    def clear(self, cap):
        glClear(cap)

    def viewport(self, x, y, width, height):
        glViewport(x, y, width, height)

    def clear_background(self):
        self.clear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def disable(self, cap):
        glDisable(cap)

    def set_line_width(self, width):
        glLineWidth(width)

    def set_polygon_mode(self, face, mode):
        glPolygonMode(face, mode)

    def set_color(self, rgba):
        glColor4f(*rgba)

    def read_pixels(self, depth: ndarray[Any, dtype[Any]] | ndarray[Any, dtype[generic]], x: int, y_gl: int):
        glReadPixels(x, y_gl, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, depth)

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
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)

        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGB,
            width, height, 0,
            GL_RGB, GL_UNSIGNED_BYTE, data
        )

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

        glGenerateMipmap(GL_TEXTURE_2D)

        return tex

    def delete_texture(self, tex_id: int):
        glDeleteTextures([tex_id])


class ModernGLBackend(GLBackend, ABC):
    """Legacy GL Backend"""

    def enable(self, cap):
        glEnable(cap)

    def clear(self, cap):
        glClear(cap)

    def viewport(self, x, y, width, height):
        glViewport(x, y, width, height)

    def enable_multisample(self):
        glEnable(GL_MULTISAMPLE)

    def clear_background(self):
        self.clear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def read_pixels(self, depth: ndarray[Any, dtype[Any]] | ndarray[Any, dtype[generic]], x: int, y_gl: int):
        glReadPixels(x, y_gl, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, depth)

    def enable_clip0(self):
        self.enable(GL_CLIP_DISTANCE0)

    def enable_clip1(self):
        self.enable(GL_CLIP_DISTANCE1)

    def clear_color(self, clear_color):
        glClearColor(*clear_color)

    def disable(self, cap):
        glDisable(cap)

    def set_line_width(self, width):
        glLineWidth(width)

    def set_polygon_mode(self, face, mode):
        glPolygonMode(face, mode)

    def set_color(self, rgba):
        glColor4f(*rgba)

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
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)

        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGB,
            width, height, 0,
            GL_RGB, GL_UNSIGNED_BYTE, data
        )

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

        glGenerateMipmap(GL_TEXTURE_2D)

        return tex

    def delete_texture(self, tex_id: int):
        glDeleteTextures([tex_id])

    def set_blend(self, enabled: bool):
        self.enable(GL.GL_BLEND) if enabled else self.disable(GL.GL_BLEND)

    def set_depth_test(self, enabled: bool):
        (
            self.enable(GL.GL_DEPTH_TEST)
            if enabled
            else self.disable(GL.GL_DEPTH_TEST)
        )

    def set_depth_write(self, enabled: bool):
        GL.glDepthMask(bool(enabled))

    def set_cull_face(self, enabled: bool):
        (
            self.enable(GL.GL_CULL_FACE)
            if enabled
            else self.disable(GL.GL_CULL_FACE)
        )

    def set_polygon_mode(self, *args):
        if len(args) == 1:
            face, mode = GL.GL_FRONT_AND_BACK, args[0]
        elif len(args) == 2:
            face, mode = args
        else:
            raise TypeError("set_polygon_mode expects mode or face, mode")
        super().set_polygon_mode(face, mode)

    def set_lighting(self, enabled: bool):
        (
            self.enable(GL.GL_LIGHTING)
            if enabled
            else self.disable(GL.GL_LIGHTING)
        )

    def set_uniform_color(self, color: tuple, alpha: float):
        r, g, b = color[:3]
        self.set_color((r, g, b, 1.0 - alpha))

