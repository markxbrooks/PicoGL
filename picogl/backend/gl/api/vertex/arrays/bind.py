"""
Binds a vertex array object for subsequent OpenGL operations.

This function wraps the `glBindVertexArray` function provided by OpenGL, allowing
the caller to bind a vertex array object identified by its integer ID. Binding
a vertex array object makes it the active array object for rendering and other
OpenGL operations.

Parameters
----------
vao : int
    The identifier of the vertex array object to bind. Must be a non-negative
    integer.

Raises
------
AssertionError
    If `vao` is None or a negative value.
"""

from OpenGL.raw.GL.VERSION.GL_3_0 import glBindVertexArray


def gl_bind_vertex_array(vao: int) -> None:
    """
    Binds a vertex array object (VAO) in OpenGL.

    This function wraps the OpenGL `glBindVertexArray` function to bind a
    specific VAO for subsequent OpenGL operations.

    Parameters:
    vao: int
        The ID of the vertex array object to bind. Must not be None and
        must be a non-negative integer.
    """
    assert vao is not None and vao >= 0
    glBindVertexArray(vao)
