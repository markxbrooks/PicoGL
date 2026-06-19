"""
Open GL draw wrappers
"""

import ctypes

from OpenGL.raw.GL.VERSION.GL_1_1 import (
    glDrawArrays,
    glDrawElements, )

from picogl.state.draw_mode import GLDrawMode, GLIndexType


def gl_draw_arrays(index_count: int,
                   mode: GLDrawMode, first: int = 0):
    """gl draw arrays"""
    glDrawArrays(mode, first, index_count)


def gl_draw_elements(index_count: int,
                     dtype: int | None = GLIndexType.UNSIGNED_INT,
                     mode: GLDrawMode | None = GLDrawMode.TRIANGLES,
                     offset: int = 0):
    """gl draw elements"""
    glDrawElements(mode, index_count, dtype, ctypes.c_void_p(offset))


