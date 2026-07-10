"""
This module provides a function to determine if a given handle
is a valid OpenGL Vertex Array Object.

It utilizes the OpenGL function glIsVertexArray to perform
the check and returns the result as a boolean value.
"""

from typing import Any

from OpenGL.raw.GL.VERSION.GL_3_0 import glIsVertexArray


def gl_is_vertex_array(handle: Any | None) -> bool:
    """
    Determines if a given handle corresponds to a valid OpenGL vertex array object.

    The function checks whether the provided handle references a valid OpenGL
    vertex array object. If the handle is valid and represents a vertex array object,
    it returns True; otherwise, it returns False.

    Parameters:
    handle (Any | None): A handle that is potentially a reference to an OpenGL vertex
        array object. Can be of any type or None.

    Returns:
    bool: True if the given handle is a valid OpenGL vertex array object,
        otherwise False.
    """
    return bool(glIsVertexArray(handle))
