"""
gl bind buffer wrapper

"""

import ctypes
from typing import Optional

from OpenGL.GL import glVertexAttribPointer

from picogl.boolean import GLBoolean
from picogl.numerical import GLNumeric


def gl_vertex_attrib_pointer(
    index: int,
    size: int,
    num_type: GLNumeric = GLNumeric.FLOAT,
    normalized: GLBoolean = GLBoolean.FALSE,
    stride: int = 0,
    offset: Optional[int] = None,
) -> None:
    """
    gl_bind_vertex_array

    :param index: int
    :param size: int
    :param num_type: int
    :param normalized: int
    :param stride: int
    :param offset: int
    """
    assert index >= 0
    pointer = None if offset is None else ctypes.c_void_p(offset)
    glVertexAttribPointer(index, size, num_type, normalized, stride, pointer)
