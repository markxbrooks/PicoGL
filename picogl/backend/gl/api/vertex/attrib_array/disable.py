"""
This module provides a function for disabling a vertex attribute array
in OpenGL.

The function is a wrapper around OpenGL's glDisableVertexAttribArray,
and it disables the specified vertex attribute array based on the given
index. This action can be useful when managing vertex attribute pointers
while rendering graphics using OpenGL.
"""
from OpenGL.raw.GL.VERSION.GL_2_0 import glDisableVertexAttribArray


def gl_disable_vertex_attrib_array(index: int) -> None:
    """
    Disables a generic vertex attribute array at index 0, making the corresponding index of the attribute array
    unavailable for rendering operations.

    Raises:
        RuntimeError: If called in an invalid OpenGL context.
    """
    glDisableVertexAttribArray(index)
