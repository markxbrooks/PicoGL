"""
gl disable vertex array wrapper

"""

from typing import Any

from OpenGL.GL import glGetIntegerv


def gl_get_integerv(val) -> Any:
    """get integer value"""
    return glGetIntegerv(val)