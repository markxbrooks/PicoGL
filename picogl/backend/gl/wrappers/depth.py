"""
depth functions
"""

from OpenGL.GL import glGetBooleanv
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_DEPTH_WRITEMASK, glDepthMask, glDepthFunc

from picogl.boolean import GLBoolean

from OpenGL.raw.GL.VERSION.GL_1_0 import glClearDepth


def gl_depth_func(func: "GLDepthFunc") -> None:
    glDepthFunc(func)


def gl_get_depth_mask():
    return glGetBooleanv(GL_DEPTH_WRITEMASK)


def gl_set_depth_mask(flag):
    glDepthMask(GLBoolean.TRUE if flag else GLBoolean.FALSE)


def gl_clear_depth(depth):
    glClearDepth(depth)
