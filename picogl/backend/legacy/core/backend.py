from OpenGL.GL import glDrawElements, glTexCoordPointer
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_FLOAT, GL_TEXTURE_2D,
                                          GL_UNSIGNED_INT, glColor4f,
                                          glDisable, glEnable, glLineWidth,
                                          glPolygonMode)
from OpenGL.raw.GL.VERSION.GL_1_1 import (GL_COLOR_ARRAY, GL_NORMAL_ARRAY,
                                          GL_TEXTURE_COORD_ARRAY,
                                          GL_VERTEX_ARRAY, glBindTexture,
                                          glColorPointer, glEnableClientState,
                                          glNormalPointer, glVertexPointer)
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