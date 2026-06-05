from OpenGL.GL import glDrawElements, glTexCoordPointer
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_FLOAT,
                                          GL_UNSIGNED_INT, glColor4f,
                                          glDisable, glEnable, glLineWidth,
                                          glPolygonMode, glIsEnabled, glBlendFunc, GL_LINEAR_MIPMAP_LINEAR)
from OpenGL.raw.GL.VERSION.GL_1_1 import (GL_COLOR_ARRAY, GL_NORMAL_ARRAY,
                                          GL_TEXTURE_COORD_ARRAY,
                                          GL_VERTEX_ARRAY,
                                          glColorPointer, glEnableClientState,
                                          glNormalPointer, glVertexPointer, glDeleteTextures)
from OpenGL.GL import (GL_CLAMP_TO_EDGE, GL_LINEAR, GL_RGB,
                       GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                       GL_TEXTURE_MIN_FILTER, GL_TEXTURE_WRAP_S,
                       GL_TEXTURE_WRAP_T, GL_UNSIGNED_BYTE,
                       glBindTexture, glGenTextures, glTexImage2D,
                       glTexParameteri)
from OpenGL.GL.framebufferobjects import glGenerateMipmap
from picogl.backend.opengl import GLBackend


class LegacyGLBackend(GLBackend):
    """Legacy GL Backend"""
    def enable(self, cap):
        glEnable(cap)

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
        glTexCoordPointer(2, GL_FLOAT, 0, data)

    def draw_elements(self, mode, indices):
        glDrawElements(mode, len(indices), GL_UNSIGNED_INT, indices)

    def bind_texture(self, texture_id):
        glBindTexture(GL_TEXTURE_2D, texture_id)

    def is_enabled(self, cap):
        return bool(glIsEnabled(cap))

    def set_blend_func(self, src, dst):
        glBlendFunc(src, dst)

    def create_texture(self, width, height, data) -> int:
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

    def bind_texture(self, tex_id: int, slot: int = 0):
        glBindTexture(GL_TEXTURE_2D, tex_id)
