"""
gl bind buffer wrapper

"""

from typing import Any, Callable

from OpenGL.GL import glGenVertexArrays
from OpenGL.raw.GL.VERSION.GL_3_0 import glBindVertexArray, glIsVertexArray


def gl_bind_vertex_array(vao: int):
    """
    gl_bind_vertex_array

    :param vao: int VAO handle; ``0`` unbinds the current VAO.
    """
    assert vao is not None and vao >= 0
    glBindVertexArray(vao)


def gl_is_vertex_array(handle: Any | None) -> bool:
    return bool(glIsVertexArray(handle))


def gl_gen_vertex_arrays() -> Callable:
    return glGenVertexArrays
