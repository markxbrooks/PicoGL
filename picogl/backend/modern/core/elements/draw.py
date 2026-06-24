"""
draw elements
"""
from contextlib import contextmanager

from picogl.backend.gl.enums import GLDrawMode, GLNumeric
from picogl.backend.gl.wrappers import gl_draw_elements
from picogl.backend.gl.wrappers.vertex_array import gl_bind_vertex_array


def draw_elements(
    vao: int, index_count: int, mode: int = GLDrawMode.LINES, index_type: int = GLNumeric.UNSIGNED_INT
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
    
    
@contextmanager
def bound_vertex_array(vao):
    """bound vertec array"""
    
    try:
       gl_bind_vertex_array(vao)
       yield:
    
    finally:
       gl_bind_vertex_array(0)
    
