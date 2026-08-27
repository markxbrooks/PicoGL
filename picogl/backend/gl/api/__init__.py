"""
This module provides bindings and utilities for interacting with OpenGL buffers,
vertex arrays, texture, client states, and draw operations. These functions
facilitate working with OpenGL through abstractions and are commonly utilized in
graphics programming for setting up and rendering graphics pipelines.

Exports a variety of OpenGL utility functions, including buffer operations,
vertex and texture handling, and client state management.
"""

from picogl.backend.gl.api.buffer.data import gl_buffer_data
from picogl.backend.gl.api.buffer.generate import gl_generate_buffers
from picogl.backend.gl.api.buffer.upload import (
    gl_upload_float_buffer,
    gl_upload_ushort_buffer,
)
from picogl.backend.gl.api.client_state import (
    gl_disable_legacy_client_state,
    gl_enable_legacy_client_state,
)
from picogl.backend.gl.api.draw import gl_draw_arrays, gl_draw_elements
from picogl.backend.gl.api.draw.indexed import gl_bind_elements
from picogl.backend.gl.api.flush import gl_flush
from picogl.backend.gl.api.pointer import (
    gl_color_array_pointer,
    gl_color_pointer_from_spec,
    gl_normal_array_pointer,
    gl_normal_pointer_from_spec,
    gl_texcoord_array_pointer,
    gl_vertex_array_pointer,
    gl_vertex_pointer_from_spec,
)
from picogl.backend.gl.api.vertex.arrays.bind import gl_bind_vertex_array
from picogl.backend.gl.api.vertex.attrib_array.bind import gl_bind_array_buffer
from picogl.backend.gl.api.vertex.attrib_array.bound import (
    gl_bound_vertex_attrib_arrays,
)
from picogl.backend.gl.api.vertex.attrib_pointer import gl_vertex_attrib_pointer
from picogl.backend.gl.api.vertex.enable_array import gl_enable_vertex_array
from picogl.backend.gl.api.vertex.generate_array import gl_generate_vertex_array
from picogl.backend.gl.api.vertex.normal_3f import gl_normal_3f
from picogl.backend.gl.api.vertex.vertex_3f import (
    gl_vertex_3f,
    gl_vertex_coord,
    gl_vertex_line,
)

from .buffer.bind import gl_bind_buffer
from .get_integerv import gl_get_integerv
from .texture.active import gl_active_texture, gl_get_active_texture0
from .texture.bind import gl_bind_texture
from .texture.generate import gl_gen_textures
from .texture.image import gl_compressed_tex_image, gl_teximage2d, gl_teximage3d
from .texture.mipmap import gl_generate_mipmap
from .texture.parameter import gl_tex_parameter

__all__ = [
    "gl_bind_array_buffer",
    "gl_bind_buffer",
    "gl_bind_elements",
    "gl_bound_vertex_attrib_arrays",
    "gl_buffer_data",
    "gl_disable_legacy_client_state",
    "gl_enable_legacy_client_state",
    "gl_enable_vertex_array",
    "gl_draw_arrays",
    "gl_draw_elements",
    "gl_flush",
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
    "gl_normal_3f",
    "gl_tex_parameter",
    "gl_color_array_pointer",
    "gl_color_pointer_from_spec",
    "gl_normal_array_pointer",
    "gl_normal_pointer_from_spec",
    "gl_texcoord_array_pointer",
    "gl_upload_float_buffer",
    "gl_upload_ushort_buffer",
    "gl_vertex_3f",
    "gl_vertex_coord",
    "gl_vertex_line",
    "gl_vertex_array_pointer",
    "gl_vertex_pointer_from_spec",
    "gl_vertex_attrib_pointer",
]
