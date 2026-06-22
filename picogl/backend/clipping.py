from contextlib import contextmanager

from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_CLIP_PLANE0,
    GL_CLIP_PLANE1,
    glDisable,
    glEnable,
)


@contextmanager
def gl_clipping_planes(enabled: bool):
    """
    Context manager to enable/disable clipping planes safely.
    Enables clipping planes when True, otherwise disables them.
    Restores previous state at exit if you decide to extend it later.
    """
    try:
        if enabled:
            glEnable(GL_CLIP_PLANE0)
            glEnable(GL_CLIP_PLANE1)
        else:
            glDisable(GL_CLIP_PLANE0)
            glDisable(GL_CLIP_PLANE1)
        yield
    finally:
        # Optional: ensure a known safe state after use
        glDisable(GL_CLIP_PLANE0)
        glDisable(GL_CLIP_PLANE1)
