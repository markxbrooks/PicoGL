"""
depth functions
"""

from OpenGL.GL import glGetBooleanv
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_DEPTH_WRITEMASK, glDepthMask

from picogl.boolean import GLBoolean


def gl_get_depth_mask():
    return glGetBooleanv(GL_DEPTH_WRITEMASK)


def gl_set_depth_mask(flag):
    glDepthMask(GLBoolean.TRUE if flag else GLBoolean.FALSE)
