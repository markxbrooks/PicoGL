"""
gl bind buffer wrapper

"""

from typing import Any

from OpenGL.raw.GL.VERSION.GL_1_5 import glIsBuffer


def buffer_name(handle: Any) -> int:
    """Return a GL buffer name as a Python int.

    ``glGenBuffers(1)`` returns a length-1 array. Passing that array through
    to ``glIsBuffer`` does not name the buffer, so a later unbind reports
    the handle as invalid.

    :param handle: Buffer name, or ``None``
    :return: Name, or ``0`` when *handle* is empty
    """
    if handle is None:
        return 0
    try:
        return int(handle)
    except (TypeError, ValueError):
        try:
            return int(handle[0])
        except (TypeError, ValueError, IndexError, KeyError):
            return 0


def gl_is_buffer(handle: Any) -> Any:
    """Return whether *handle* is a buffer object in the current context."""
    name = buffer_name(handle)
    if name <= 0:
        return False
    return glIsBuffer(name)
