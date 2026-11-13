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

from picogl.backend.gl.api.buffer.check_is import buffer_name


def gl_generate_buffers(num: int = 1) -> Any:
    """Generate buffer object names.

    A request for one name returns a Python ``int``. ``glGenBuffers(1)``
    otherwise returns a length-1 array, which ``glIsBuffer`` does not accept
    as a buffer name.

    :param num: How many names to generate
    :return: One buffer name, or the array of names when *num* is greater than 1
    """
    assert num > 0
    names = glGenBuffers(num)
    if num == 1:
        return buffer_name(names)
    return names
