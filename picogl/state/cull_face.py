"""
GL Cull Face
"""
from contextlib import contextmanager

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_CULL_FACE, glDisable, glEnable,
                                          glIsEnabled)


class GLCullFace:
    """Cull face state wrapper"""

    @staticmethod
    def is_enabled() -> bool:
        return glIsEnabled(GL_CULL_FACE)

    @staticmethod
    def enable() -> None:
        glEnable(GL_CULL_FACE)

    @staticmethod
    def disable() -> None:
        glDisable(GL_CULL_FACE)


def gl_capability_enabled(capability: int) -> bool:
    return bool(glIsEnabled(capability))


def gl_set_capability(capability: int, enabled: bool) -> None:
    if enabled:
        glEnable(capability)
    else:
        glDisable(capability)


@contextmanager
def preserve_gl_capability(capability: int):
    was_enabled = gl_capability_enabled(capability)
    try:
        yield
    finally:
        gl_set_capability(capability, was_enabled)
@contextmanager
def cull_face(enabled: bool = True):
    with preserve_gl_capability(GL_CULL_FACE):
        gl_set_capability(GL_CULL_FACE, enabled)
        yield