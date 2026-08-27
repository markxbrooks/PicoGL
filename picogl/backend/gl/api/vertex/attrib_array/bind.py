"""Bind an ARRAY buffer and configure its vertex attribute pointer."""

from __future__ import annotations

from picogl.backend.gl.api.buffer.bind import gl_bind_buffer
from picogl.backend.gl.api.vertex.attrib_array.pointer import gl_vertex_attrib_pointer
from picogl.backend.gl.enums import GLBufferTarget, GLNumeric
from picogl.boolean import GLBoolean


def gl_bind_array_buffer(
    buffer,
    index: int = 0,
    size: int = 3,
    stride: int = 0,
) -> None:
    """Bind an ARRAY buffer and set its vertex attrib pointer."""
    gl_bind_buffer(GLBufferTarget.ARRAY, buffer)
    gl_vertex_attrib_pointer(
        index, size, GLNumeric.FLOAT, GLBoolean.FALSE, stride, None
    )
