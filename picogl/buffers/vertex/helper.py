"""
Open GL wrappers
"""

import ctypes

from OpenGL.raw.GL.VERSION.GL_1_1 import (
    glDrawArrays,
    glDrawElements, glColorPointer, glNormalPointer, glVertexPointer, glEnableClientState,
)
from OpenGL.raw.GL.VERSION.GL_1_5 import glBindBuffer

from picogl.buffers.attributes import AttributeSpec
from picogl.state.client import GLClientState
from picogl.state.draw_mode import GLDrawMode, GLIndexType


def gl_draw_arrays(index_count: int,
                   mode: GLDrawMode, first: int = 0):
    """gl draw arrays"""
    glDrawArrays(mode, first, index_count)


def gl_draw_elements(index_count: int,
                     dtype: int = GLIndexType.UNSIGNED_INT,
                     mode: GLDrawMode = GLDrawMode.TRIANGLES,
                     offset: int = 0):
    """gl draw elements"""
    glDrawElements(mode, index_count, dtype, ctypes.c_void_p(offset))


def gl_bind_buffer(target, ebo_id: int | None):
    """gl bind buffer"""
    glBindBuffer(target, ebo_id)


def gl_color_pointer(attr: AttributeSpec):
    """gl color pointer"""
    glColorPointer(attr.size, attr.type, attr.stride, ctypes.c_void_p(attr.offset))


def gl_normal_pointer(attr: AttributeSpec):
    """gl normal pointer"""
    glNormalPointer(attr.type, attr.stride, ctypes.c_void_p(attr.offset))


def gl_vertex_pointer(attr: AttributeSpec):
    """gl legacy client state"""
    glVertexPointer(attr.size, attr.type, attr.stride, ctypes.c_void_p(attr.offset))


def gl_legacy_client_state(state: GLClientState):
    """gl legacy client state"""
    glEnableClientState(state)
