"""
gl bind buffer wrapper

"""

from typing import Any

from OpenGL.raw.GL.VERSION.GL_1_5 import glIsBuffer


def gl_is_buffer(handle) -> Any:
    """gl is buffer"""
    return glIsBuffer(handle)
