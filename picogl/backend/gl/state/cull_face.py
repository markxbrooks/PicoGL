"""
gl Cull Face
"""

from contextlib import contextmanager

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_CULL_FACE, glDisable, glEnable, glIsEnabled
from backend.gl.api.capabilities import GLCapabilities
from backend.gl.api.enable import gl_enable, gl_disable


class GLCullFace:
    """Cull face state wrapper"""

    @staticmethod
    def is_enabled() -> bool:
        return glIsEnabled(GL_CULL_FACE)

    @staticmethod
    def enable() -> None:
        gl_enable(GL_CULL_FACE)

    @staticmethod
    def disable() -> None:
        gl_disable(GL_CULL_FACE)


def gl_capability_enabled(capability: int) -> bool:
    return bool(glIsEnabled(capability))


def gl_set_capability(capability: GLCapabilities, enabled: bool) -> None:
    if enabled:
        gl_enable(capability)
    else:
        gl_disable(capability)


@contextmanager
def preserve_gl_capability(capability: GLCapabilities):
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
