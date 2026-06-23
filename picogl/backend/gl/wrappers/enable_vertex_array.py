"""
gl enable vertex array wrapper

"""

from typing import Any

from OpenGL.GL import gl_enableVertexAttribArray


def gl_enable_vertex_array(location: int) -> Any:
    """
    gl_enable_vertex_array

    :param location: int
    """
    assert location >= 0
    gl_enableVertexAttribArray(location)
