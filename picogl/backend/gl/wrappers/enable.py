"""
gl enable disable is enabled
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glDisable, glEnable, glIsEnabled



def gl_enable(cap):
    glEnable(cap)


def gl_disable(cap):
    glDisable(cap)


def gl_is_enabled(cap):
    return glIsEnabled(cap)
