from contextlib import contextmanager

from OpenGL.GL import glIsEnabled
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_BLEND, GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, glBlendFunc, glDisable, glEnable

@contextmanager
def gl_blend():
    was_enabled = glIsEnabled(GL_BLEND)
    try:
        if not was_enabled:
            glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        yield
    finally:
        if not was_enabled:
            glDisable(GL_BLEND)
