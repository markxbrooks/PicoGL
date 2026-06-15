from OpenGL.raw.GL.VERSION.GL_1_0 import glLineWidth, GL_FRONT_AND_BACK, glPolygonMode

from picogl.backend.state import gl_value


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
