"""Thin OpenGL call wrappers (legacy client state, pointers, buffers, draws)."""

from picogl.wrappers.buffer import gl_bind_buffer
from picogl.wrappers.client_state import (
    gl_disable_legacy_client_state,
    gl_enable_legacy_client_state,
)
from picogl.wrappers.data import gl_buffer_data
from picogl.wrappers.draw import gl_draw_arrays, gl_draw_elements
from picogl.wrappers.enable_vertex_array import gl_enable_vertex_array
from picogl.wrappers.generate_buffers import gl_generate_buffers
from picogl.wrappers.generate_vertex_array import gl_generate_vertex_array
from picogl.wrappers.pointer import (
    gl_color_array_pointer,
    gl_color_pointer_from_spec,
    gl_normal_array_pointer,
    gl_normal_pointer_from_spec,
    gl_texcoord_array_pointer,
    gl_vertex_array_pointer,
    gl_vertex_pointer_from_spec,
)
from picogl.wrappers.texture import (
    gl_compressed_tex_image,
    gl_generate_mipmap,
    gl_tex_parameter,
    gl_teximage2d,
    gl_teximage3d,
)
from picogl.wrappers.vertex_array import gl_bind_vertex_array
from picogl.wrappers.vertex_attrib_pointer import gl_vertex_attrib_pointer

__all__ = [
    "gl_bind_buffer",
    "gl_buffer_data",
    "gl_disable_legacy_client_state",
    "gl_enable_legacy_client_state",
    "gl_enable_vertex_array",
    "gl_draw_arrays",
    "gl_draw_elements",
    "gl_generate_buffers",
    "gl_generate_mipmap",
    "gl_generate_vertex_array",
    "gl_bind_vertex_array",
    "gl_compressed_tex_image",
    "gl_teximage2d",
    "gl_teximage3d",
    "gl_tex_parameter",
    "gl_color_array_pointer",
    "gl_color_pointer_from_spec",
    "gl_normal_array_pointer",
    "gl_normal_pointer_from_spec",
    "gl_texcoord_array_pointer",
    "gl_vertex_array_pointer",
    "gl_vertex_pointer_from_spec",
    "gl_vertex_attrib_pointer",
]
