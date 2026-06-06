"""
GL Cull Face
"""

from typing import Any

from OpenGL.raw.GL.VERSION.GL_1_0 import glIsEnabled, GL_CULL_FACE, glEnable, glDisable


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


def gl_get_cull_face_enabled() -> Any:
    return glIsEnabled(GL_CULL_FACE)


def gl_enable_cull_face():
    glEnable(GL_CULL_FACE)


def gl_disable_cull_face():
    glDisable(GL_CULL_FACE)
