from OpenGL.GL import (
    glColorPointer,
    glNormalPointer,
    glTexCoordPointer,
    glVertexPointer,
)
from OpenGL.raw.GL._types import GL_FLOAT
from OpenGL.raw.GL.KHR.debug import GL_VERTEX_ARRAY
from OpenGL.raw.GL.VERSION.GL_1_1 import (
    GL_COLOR_ARRAY,
    GL_NORMAL_ARRAY,
    GL_TEXTURE_COORD_ARRAY,
    glDisableClientState,
    glEnableClientState,
)


class LegacyAttributeBinder:
    """Legacy client-state and vertex attribute pointer operations."""

    @staticmethod
    def enable_vertex_array():
        glEnableClientState(GL_VERTEX_ARRAY)

    @staticmethod
    def disable_vertex_array():
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
