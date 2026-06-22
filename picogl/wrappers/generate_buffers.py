"""
gl generate buffer wrapper

"""

from typing import Any

from OpenGL.GL import glGenBuffers


def gl_generate_buffers(num: int = 1) -> Any:
    """
    gl_generate_buffers

    :param num: int
    """
    assert num > 0
    return glGenBuffers(num)
