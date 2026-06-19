"""Thin OpenGL call wrappers (legacy client state, pointers, buffers, draws)."""

from picogl.wrappers.buffer import gl_bind_buffer
from picogl.wrappers.client_state import (
    gl_disable_legacy_client_state,
    gl_enable_legacy_client_state,
)
from picogl.wrappers.data import gl_buffer_data
from picogl.wrappers.draw import gl_draw_arrays, gl_draw_elements
from picogl.wrappers.pointer import (
    gl_color_array_pointer,
    gl_color_pointer_from_spec,
    gl_normal_array_pointer,
    gl_normal_pointer_from_spec,
    gl_texcoord_array_pointer,
    gl_vertex_array_pointer,
    gl_vertex_pointer_from_spec,
)

__all__ = [
    "gl_bind_buffer",
    "gl_buffer_data",
    "gl_disable_legacy_client_state",
    "gl_enable_legacy_client_state",
    "gl_draw_arrays",
    "gl_draw_elements",
    "gl_color_array_pointer",
    "gl_color_pointer_from_spec",
    "gl_normal_array_pointer",
    "gl_normal_pointer_from_spec",
    "gl_texcoord_array_pointer",
    "gl_vertex_array_pointer",
    "gl_vertex_pointer_from_spec",
]
