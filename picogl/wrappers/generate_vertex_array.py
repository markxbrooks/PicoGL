"""
gl generate buffer wrapper

"""
from typing import Any

from OpenGL.GL import glGenVertexArrays

def gl_generate_vertex_array(num: int=1) -> Any:
    """
    gl_generate_vertex_array

    :param num: int
    """
    assert num > 0
    return glGenVertexArrays(num)
