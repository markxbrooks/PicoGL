from OpenGL.GL import (GL_POINT_SIZE_RANGE, glGetFloatv,
                       glLineWidth, glPointSize,
                       glPolygonMode)
from OpenGL.raw.GL.VERSION.GL_1_1 import glPolygonOffset

from picogl.backend.state import gl_value
from picogl.state.fill import GLFace


class GLRasterDriver:
    """Fixed-function raster state operations."""

    @staticmethod
    def set_line_width(width):
        glLineWidth(width)

    @staticmethod
    def set_point_size(size):
        glPointSize(float(size))

    @staticmethod
    def get_point_size_range() -> tuple[float, float]:
        min_size, max_size = glGetFloatv(GL_POINT_SIZE_RANGE)
        return float(min_size), float(max_size)

    @classmethod
    def set_clamped_point_size(cls, size):
        min_size, max_size = cls.get_point_size_range()
        cls.set_point_size(max(min_size, min(max_size, float(size))))

    @staticmethod
    def set_polygon_offset(factor, units):
        glPolygonOffset(float(factor), float(units))

    @staticmethod
    def set_polygon_mode(*args):
        if len(args) == 1:
            face, mode = GLFace.FRONT_AND_BACK, args[0]
        elif len(args) == 2:
            face, mode = args
        else:
            raise TypeError("set_polygon_mode expects mode or face, mode")
        glPolygonMode(gl_value(face), gl_value(mode))
