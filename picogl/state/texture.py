"""
GL Draw Mode
"""

from contextlib import contextmanager
from dataclasses import dataclass
from enum import IntEnum

from OpenGL.GL import glActiveTexture, GL_TEXTURE_2D, glEnable, glBindTexture, glDisable, glIsEnabled, glGetIntegerv, GL_TEXTURE_BINDING_2D, GL_TEXTURE0, GL_ACTIVE_TEXTURE


class GLTexture(IntEnum):
    """GL Draw Mode"""
    TEXTURE_2D = GL_TEXTURE_2D

    @classmethod
    def choices(cls):
        return [m.value for m in cls]


@dataclass(frozen=True)
class TexCoord2f:
    u: float
    v: float


@contextmanager
def texture2d_legacy_manager():
    was_enabled = glIsEnabled(GL_TEXTURE_2D)
    previous_binding = glGetIntegerv(GL_TEXTURE_BINDING_2D)

    try:
        if not was_enabled:
            glEnable(GL_TEXTURE_2D)
        yield
    finally:
        glBindTexture(GL_TEXTURE_2D, previous_binding)
        if not was_enabled:
            glDisable(GL_TEXTURE_2D)


@contextmanager
def bound_texture(texture_id, unit=GL_TEXTURE0):
    prev_active = glGetIntegerv(GL_ACTIVE_TEXTURE)
    glActiveTexture(unit)

    prev = glGetIntegerv(GL_TEXTURE_BINDING_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id or 0)

    try:
        yield
    finally:
        glBindTexture(GL_TEXTURE_2D, prev)
        glActiveTexture(prev_active)
