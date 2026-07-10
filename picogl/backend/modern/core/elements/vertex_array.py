"""
vao context manager
"""

from contextlib import contextmanager

from picogl.backend.gl.api.vertex.vertex_array import gl_bind_vertex_array


@contextmanager
def bound_vertex_array(vao: int):
    """Context manager to bind a VAO for a block and restore previous binding."""
    # Optional: save current binding if you want to restore the exact previous state
    gl_bind_vertex_array(vao)
    try:
        yield
    finally:
        gl_bind_vertex_array(0)
