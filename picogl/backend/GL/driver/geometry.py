from OpenGL.GL import glDrawElements
from OpenGL.raw.GL._types import GL_UNSIGNED_INT

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
