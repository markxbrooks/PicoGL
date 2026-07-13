"""
A utility function for enabling a vertex attribute array in OpenGL.

This module provides a wrapper function for the OpenGL function
`glEnableVertexAttribArray`, which is used to enable a generic vertex
attribute array.

Functions:
- gl_enable_vertex_attrib_array(handle): Enables a vertex attribute
  array using the provided handle.
"""

from OpenGL.raw.GL.VERSION.GL_2_0 import glEnableVertexAttribArray


def gl_enable_vertex_attrib_array(index: int):
    """
    Enables a generic vertex attribute array.

    This function wraps the OpenGL functionality to enable the specified vertex
    attribute array, which is identified by its handle.

    Parameters:
    handle (int): The index of the generic vertex attribute to be enabled.
                  This typically corresponds to a location bound to a vertex shader
                  attribute.

    Returns:
    None
    """
    return glEnableVertexAttribArray(index)
