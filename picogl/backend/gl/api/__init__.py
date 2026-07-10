"""
Thin OpenGL call wrappers (legacy client state, pointers, buffers, draws).
"""

from .buffer.bind import gl_bind_buffer
from picogl.backend.gl.api.buffer.data import gl_buffer_data
from picogl.backend.gl.api.client_state import (
    gl_disable_legacy_client_state, gl_enable_legacy_client_state)
from picogl.backend.gl.api.draw import gl_draw_arrays, gl_draw_elements
from picogl.backend.gl.api.vertex.enable_array import \
    gl_enable_vertex_array
from picogl.backend.gl.api.buffer.generate import gl_generate_buffers
from picogl.backend.gl.api.vertex.generate_array import \
    gl_generate_vertex_array
from picogl.backend.gl.api.pointer import (gl_color_array_pointer,
                                           gl_color_pointer_from_spec,
                                           gl_normal_array_pointer,
                                           gl_normal_pointer_from_spec,
                                           gl_texcoord_array_pointer,
                                           gl_vertex_array_pointer,
                                           gl_vertex_pointer_from_spec)
from picogl.backend.gl.api.texture import (gl_active_texture,
                                           gl_bind_texture,
                                           gl_compressed_tex_image,
                                           gl_gen_textures,
                                           gl_generate_mipmap,
                                           gl_get_active_texture0,
                                           gl_tex_parameter,
                                           gl_teximage2d, gl_teximage3d)
from picogl.backend.gl.api.vertex.array import gl_bind_vertex_array
from picogl.backend.gl.api.vertex.attrib_pointer import \
    gl_vertex_attrib_pointer

from .get_integerv import gl_get_integerv

__all__ = [
    "gl_bind_buffer",
    "gl_buffer_data",
    "gl_disable_legacy_client_state",
    "gl_enable_legacy_client_state",
    "gl_enable_vertex_array",
    "gl_draw_arrays",
    "gl_draw_elements",
    "gl_generate_buffers",
    "gl_active_texture",
    "gl_bind_texture",
    "gl_generate_mipmap",
    "gl_gen_textures",
    "gl_get_active_texture0",
    "gl_generate_vertex_array",
    "gl_bind_vertex_array",
    "gl_compressed_tex_image",
    "gl_teximage2d",
    "gl_teximage3d",
    "gl_get_integerv",
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
