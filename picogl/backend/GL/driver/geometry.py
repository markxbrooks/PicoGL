from OpenGL.GL import glDrawElements
from OpenGL.raw.GL._types import GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays
from OpenGL.raw.GL.VERSION.GL_3_0 import glBindVertexArray

from picogl.backend.opengl import GLBindingStrategy
from picogl.backend.state import gl_value


class GLGeometryDriver:
    """Mesh binding and indexed draw operations."""

    def __init__(self, binding: GLBindingStrategy):
        self.binding = binding

    def draw_mesh(self, mesh, mode):
        self.binding.bind_mesh(mesh)
        self.binding.draw(mesh, gl_value(mode))

    @staticmethod
    def draw_elements(mode, indices):
        glDrawElements(gl_value(mode), len(indices), GL_UNSIGNED_INT, indices)

    @staticmethod
    def draw_bound_elements(mode, index_count: int, index_type=GL_UNSIGNED_INT, pointer=None):
        glDrawElements(gl_value(mode), int(index_count), gl_value(index_type), pointer)

    @staticmethod
    def draw_arrays(mode, first: int, count: int):
        glDrawArrays(gl_value(mode), int(first), int(count))

    @classmethod
    def draw_arrays_bound_vao(cls, vao: int, mode, first: int, count: int):
        glBindVertexArray(int(vao))
        try:
            cls.draw_arrays(mode, first, count)
        finally:
            glBindVertexArray(0)
