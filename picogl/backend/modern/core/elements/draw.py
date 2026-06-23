from OpenGL.raw.GL._types import GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LINES

from picogl.backend.gl.wrappers import gl_draw_elements
from picogl.backend.gl.wrappers.vertex_array import gl_bind_vertex_array


def draw_elements(
    vao: int, index_count: int, mode: int = GL_LINES, index_type: int = GL_UNSIGNED_INT
):
    """
    Helper method to bind a VAO and draw its elements.

    :param vao: Vertex Array Object to bind
    :param index_count: Number of indices to draw
    :param mode: Drawing gl_mode (e.g., GL_LINES, GL_TRIANGLES)
    :param index_type: Type of indices (e.g., GL_UNSIGNED_INT)
    """
    gl_bind_vertex_array(vao)
    gl_draw_elements(index_count, index_type, mode, pointer=None)
    gl_bind_vertex_array(0)
