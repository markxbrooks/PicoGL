"""Unit cube mesh (positions + UVs) for textured tutorial examples."""

from __future__ import annotations

from picogl.backend.gl.api import gl_bind_buffer, gl_generate_buffers
from picogl.backend.gl.api.buffer.upload import gl_upload_float_buffer
from picogl.backend.gl.api.draw.array import gl_draw_arrays
from picogl.backend.gl.api.vertex.attrib_array.bind import gl_bind_array_buffer
from picogl.backend.gl.api.vertex.attrib_array.bound import \
    gl_bound_vertex_attrib_arrays
from picogl.backend.gl.enums import GLBufferTarget, GLDrawMode
from picogl.utils.mesh.object_mesh import flip_texcoord_v


class CubeMesh:
    """Unit cube with position + UV buffers (non-indexed glDrawArrays)."""

    def __init__(self, vertices: list[float], texcoords: list[float]) -> None:
        self.vertices = list(vertices)
        self.texcoords = list(texcoords)
        self.vertex_buffer: int | None = None
        self.uv_buffer: int | None = None
        self._vertex_count = len(self.vertices) // 3

    def with_flipped_v(self) -> CubeMesh:
        self.texcoords = flip_texcoord_v(self.texcoords)
        return self

    def upload(self) -> None:
        self.vertex_buffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.vertex_buffer)
        gl_upload_float_buffer(self.vertices)

        self.uv_buffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.uv_buffer)
        gl_upload_float_buffer(self.texcoords)

    def draw(self) -> None:
        with gl_bound_vertex_attrib_arrays([0, 1]):
            gl_bind_array_buffer(self.vertex_buffer, index=0)
            gl_bind_array_buffer(self.uv_buffer, index=1, size=2, stride=0)
            gl_draw_arrays(self._vertex_count, GLDrawMode.TRIANGLES, first=0)
