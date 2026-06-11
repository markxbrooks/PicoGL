from contextlib import contextmanager

from OpenGL.GL import glIsEnabled, glGetIntegerv
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_BLEND, GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, glBlendFunc, glDisable, \
    glEnable, GL_BLEND_SRC, GL_BLEND_DST


@contextmanager
def gl_blend(src=GL_SRC_ALPHA, dst=GL_ONE_MINUS_SRC_ALPHA):
    was_enabled = glIsEnabled(GL_BLEND)
    prev_src = glGetIntegerv(GL_BLEND_SRC)
    prev_dst = glGetIntegerv(GL_BLEND_DST)

    try:
        if not was_enabled:
            glEnable(GL_BLEND)
        glBlendFunc(src, dst)
        yield
    finally:
        glBlendFunc(prev_src, prev_dst)
        if not was_enabled:
            glDisable(GL_BLEND)
