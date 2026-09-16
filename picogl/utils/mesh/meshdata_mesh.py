"""Adapt ``MeshData`` to ``MeshProtocol`` for TexturedMeshRenderer."""

from __future__ import annotations

from typing import Callable

import numpy as np
from OpenGL.GL import GLuint
from picogl.backend.gl.api import gl_bind_buffer, gl_generate_buffers
from picogl.backend.gl.api.buffer.data import gl_buffer_data
from picogl.backend.gl.api.buffer.upload import (
    gl_upload_float_buffer,
    gl_upload_ushort_buffer,
)
from picogl.backend.gl.api.draw.array import gl_draw_arrays
from picogl.backend.gl.api.draw.elements import gl_draw_elements
from picogl.backend.gl.api.vertex.attrib_array.bind import gl_bind_array_buffer
from picogl.backend.gl.api.vertex.attrib_array.bound import (
    gl_bound_vertex_attrib_arrays,
)
from picogl.backend.gl.enums import GLBufferTarget, GLDrawMode, GLNumeric, GLUsageHint
from picogl.renderer.meshdata import MeshData
from picogl.utils.mesh.object_mesh import flip_texcoord_v
from picogl.utils.mesh.protocol import MeshProtocol


def _as_float_list(arr) -> list[float]:
    if arr is None:
        return []
    return np.asarray(arr, dtype=np.float32).reshape(-1).tolist()


def _as_index_list(arr) -> list[int]:
    if arr is None:
        return []
    return np.asarray(arr, dtype=np.int64).reshape(-1).tolist()


def _upload_uint_buffer(data: list[int]) -> None:
    gl_buffer_data(
        GLBufferTarget.ELEMENT,
        len(data) * 4,
        (GLuint * len(data))(*data),
        GLUsageHint.STATIC_DRAW,
    )


class MeshDataMesh:
    """Position + UV adapter: ``MeshData`` → ``MeshProtocol`` upload/draw."""

    def __init__(self, data: MeshData, *, flip_v: bool = False) -> None:
        if data.vertices is None:
            raise ValueError("MeshData.vertices is required")
        if data.texcoords is None:
            raise ValueError("MeshData.texcoords (UVs) are required for textured draw")

        self.vertices = _as_float_list(data.vertices)
        self.texcoords = _as_float_list(data.texcoords)
        if flip_v:
            self.texcoords = flip_texcoord_v(self.texcoords)

        vertex_count = len(self.vertices) // 3
        if len(self.texcoords) // 2 != vertex_count:
            raise ValueError(
                f"UV count {len(self.texcoords) // 2} != vertex count {vertex_count}"
            )

        self.indices = _as_index_list(data.indices)
        self._vertex_count = vertex_count
        self._use_ushort = bool(self.indices) and max(self.indices) < 65536

        self.vertex_buffer: int | None = None
        self.uv_buffer: int | None = None
        self.index_buffer: int | None = None

    def upload(self) -> None:
        self.vertex_buffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.vertex_buffer)
        gl_upload_float_buffer(self.vertices)

        self.uv_buffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.uv_buffer)
        gl_upload_float_buffer(self.texcoords)

        if self.indices:
            self.index_buffer = gl_generate_buffers(1)
            gl_bind_buffer(GLBufferTarget.ELEMENT, self.index_buffer)
            if self._use_ushort:
                gl_upload_ushort_buffer(self.indices)
            else:
                _upload_uint_buffer(self.indices)

    def draw(self) -> None:
        with gl_bound_vertex_attrib_arrays([0, 1]):
            gl_bind_array_buffer(self.vertex_buffer, index=0)
            gl_bind_array_buffer(self.uv_buffer, index=1, size=2, stride=0)
            if self.indices and self.index_buffer is not None:
                gl_bind_buffer(GLBufferTarget.ELEMENT, self.index_buffer)
                dtype = (
                    GLNumeric.UNSIGNED_SHORT
                    if self._use_ushort
                    else GLNumeric.UNSIGNED_INT
                )
                gl_draw_elements(len(self.indices), dtype, GLDrawMode.TRIANGLES)
            else:
                gl_draw_arrays(self._vertex_count, GLDrawMode.TRIANGLES, first=0)


def meshdata_factory(data: MeshData) -> Callable[[bool], MeshProtocol]:
    """Factory for ``TexturedRendererSpec.create_mesh`` from a ``MeshData``."""

    def create_mesh(flip_v: bool) -> MeshDataMesh:
        return MeshDataMesh(data, flip_v=flip_v)

    return create_mesh
