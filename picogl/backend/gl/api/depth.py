"""
depth functions
"""

from OpenGL.GL import glGetBooleanv
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_DEPTH_WRITEMASK, glClearDepth,
                                          glDepthFunc, glDepthMask)
from picogl.boolean import GLBoolean


def gl_depth_func(func: "GLDepthFunc") -> None:
    """gl_depth_func"""
    glDepthFunc(func)


def gl_get_depth_mask() -> None:
    """gl_get_depth_mask"""
    return glGetBooleanv(GL_DEPTH_WRITEMASK)


def gl_set_depth_mask(flag) -> None:
    """gl_set_depth_mask"""
    glDepthMask(GLBoolean.TRUE if flag else GLBoolean.FALSE)


def gl_clear_depth(depth: int) -> None:
    """gl clear depth"""
    glClearDepth(depth)
