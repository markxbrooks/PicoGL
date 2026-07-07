from contextlib import contextmanager

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_CLIP_PLANE0, GL_CLIP_PLANE1
from picogl.backend.gl.wrappers.enable import gl_disable, gl_enable


@contextmanager
def gl_clipping_planes(enabled: bool):
    """
    Context manager to enable/disable clipping planes safely.
    Enables clipping planes when True, otherwise disables them.
    Restores previous state at exit if you decide to extend it later.
    """
    try:
        if enabled:
            gl_enable(GL_CLIP_PLANE0)
            gl_enable(GL_CLIP_PLANE1)
        else:
            gl_disable(GL_CLIP_PLANE0)
            gl_disable(GL_CLIP_PLANE1)
        yield
    finally:
        # Optional: ensure a known safe state after use
        gl_disable(GL_CLIP_PLANE0)
        gl_disable(GL_CLIP_PLANE1)
