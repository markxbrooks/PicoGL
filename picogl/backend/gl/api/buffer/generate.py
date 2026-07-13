"""
A utility function for generating OpenGL buffer object names.

This function provides an interface for generating one or more OpenGL
buffer object names by wrapping the OpenGL function `glGenBuffers`. It
validates the input to ensure that the requested number of buffers is
greater than zero.

:param num: The number of buffer object names to generate. Must be a
    positive integer.
:return: The generated buffer object names as returned by `glGenBuffers`.
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
