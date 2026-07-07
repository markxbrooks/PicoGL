"""
gl bind buffer wrapper

"""

from typing import Any

from OpenGL.GL import glBufferSubData
from OpenGL.raw.GL.VERSION.GL_1_5 import glBindBuffer, glIsBuffer


def gl_bind_buffer(target, ebo_id: int | None):
    """gl bind buffer"""
    glBindBuffer(target, ebo_id)


def gl_buffer_subdata(target, offset, size, data):
    """
    gl buffer subdata
    """
    glBufferSubData(target, offset, size, data)


def gl_is_buffer(handle) -> Any:
    return glIsBuffer(handle)
