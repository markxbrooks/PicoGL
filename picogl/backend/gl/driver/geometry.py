"""
Mesh binding and indexed draw operations.

Handles the binding of GPU-based meshes and facilitates drawing operations
using various strategies, including indexed draw and array draw functionalities.
Provides both static and class methods for drawing operations.

Classes:
    GLGeometryDriver: Utility for binding, drawing, and managing GPU meshes.

"""

from picogl.backend.geometry.mesh import GPUMesh
from picogl.backend.gl.enums import GLIndexType
from picogl.backend.gl.api import gl_draw_arrays, gl_draw_elements
from picogl.backend.gl.api.vertex.arrays.bind import gl_bind_vertex_array
from picogl.backend.opengl import GLBindingStrategy
from picogl.backend.state import gl_value


class GLGeometryDriver:
    """Mesh binding and indexed draw operations."""

    def __init__(self, binding: GLBindingStrategy):
        self.binding = binding

    def draw_gpu_mesh(self, gpu_mesh: GPUMesh, mode) -> None:
        """Bind and draw a uploaded GPU mesh."""
        gpu_mesh.bind()
        try:
            gpu_mesh.draw(gl_value(mode))
        finally:
            gpu_mesh.unbind()

    def draw_mesh(self, mesh, mode):
        """Deprecated: bind and draw through the binding strategy shim."""
        self.binding.bind_mesh(mesh)
        self.binding.draw(mesh, gl_value(mode))

    @staticmethod
    def draw_elements(mode, indices):
        gl_draw_elements(
            len(indices),
            GLIndexType.UNSIGNED_INT,
            mode,
            pointer=indices,
        )

    @staticmethod
    def draw_bound_elements(
        mode, index_count: int, index_type=GLIndexType.UNSIGNED_INT, pointer=None
    ):
        gl_draw_elements(int(index_count), index_type, mode, pointer=pointer)

    @staticmethod
    def draw_arrays(mode, first: int, count: int):
        gl_draw_arrays(int(count), mode, first=int(first))

    @classmethod
    def draw_arrays_bound_vao(cls, vao: int, mode, first: int, count: int):
        gl_bind_vertex_array(int(vao))
        try:
            cls.draw_arrays(mode, first, count)
        finally:
            gl_bind_vertex_array(0)
