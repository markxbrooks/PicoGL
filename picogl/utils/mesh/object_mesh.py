"""OBJ mesh with GPU VBO/EBO upload for position + UV drawing."""

from __future__ import annotations

from pathlib import Path

from picogl.backend.gl.api import gl_bind_buffer, gl_generate_buffers
from picogl.backend.gl.api.buffer.upload import (gl_upload_float_buffer,
                                                 gl_upload_ushort_buffer)
from picogl.backend.gl.api.draw.indexed import gl_bind_elements
from picogl.backend.gl.api.vertex.attrib_array.bind import gl_bind_array_buffer
from picogl.backend.gl.api.vertex.attrib_array.bound import \
    gl_bound_vertex_attrib_arrays
from picogl.backend.gl.enums import GLBufferTarget
from picogl.utils.loader.object import ObjectLoader


def flip_texcoord_v(texcoords: list[float]) -> list[float]:
    """Invert V for DDS/top-left origin (``TextureLoader.inversed_v_coords``)."""
    flipped = list(texcoords)
    for i in range(1, len(flipped), 2):
        flipped[i] = 1.0 - flipped[i]
    return flipped


class MeshObject:
    """OBJ mesh with GPU buffer upload helpers (positions + UVs + ushort indices)."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.vertices: list[float] | None = None
        self.texcoords: list[float] | None = None
        self.indices: list[int] | None = None
        self.vertex_buffer: int | None = None
        self.uv_buffer: int | None = None
        self.index_buffer: int | None = None
        self.indices_size: int = 0

    def load_mesh(self):
        if not self.path.is_file():
            raise FileNotFoundError(f"OBJ mesh not found: {self.path}")
        return ObjectLoader(str(self.path)).to_single_index_style()

    def get_mesh(self, *, flip_v: bool = False) -> MeshObject:
        mesh = self.load_mesh()
        self.vertices = mesh.vertices
        self.texcoords = (
            flip_texcoord_v(mesh.texcoords) if flip_v else list(mesh.texcoords)
        )
        self.indices = mesh.indices
        self.indices_size = len(self.indices)
        return self

    def _upload_vertices(self) -> None:
        gl_upload_float_buffer(self.vertices)

    def _upload_texcoords(self) -> None:
        gl_upload_float_buffer(self.texcoords)

    def _upload_indices(self) -> None:
        # Must be GLushort to match gl_draw_elements(..., UNSIGNED_SHORT, ...).
        gl_upload_ushort_buffer(self.indices)

    def upload(self) -> None:
        self.vertex_buffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.vertex_buffer)
        self._upload_vertices()

        self.uv_buffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.uv_buffer)
        self._upload_texcoords()

        self.index_buffer = gl_generate_buffers(1)
        # Draw-element count — not the GL buffer name from gl_generate_buffers.
        self.indices_size = len(self.indices)
        gl_bind_buffer(GLBufferTarget.ELEMENT, self.index_buffer)
        self._upload_indices()

    def draw(self) -> None:
        """Draw the mesh."""
        with gl_bound_vertex_attrib_arrays([0, 1]):
            self._draw_vertices(index=0)
            self._draw_uvs(index=1)
            self._draw_indices()

    def _draw_vertices(self, index: int = 0) -> None:
        gl_bind_array_buffer(self.vertex_buffer, index=index)

    def _draw_uvs(self, index: int = 1) -> None:
        gl_bind_array_buffer(self.uv_buffer, index=index, size=2, stride=0)

    def _draw_indices(self) -> None:
        gl_bind_elements(index_buffer=self.index_buffer, size=self.indices_size)
