"""
Provides utilities and context managers for managing OpenGL textures.

This module defines enumerations and helper classes for texture handling, along
with context managers for safely enabling and binding textures in an OpenGL
environment. It aims to simplify texture management tasks and ensure proper
state restoration after operations.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from enum import IntEnum

from OpenGL.GL import (GL_ACTIVE_TEXTURE, GL_TEXTURE_2D,
                       GL_TEXTURE_BINDING_2D, glBindTexture,
                       glDisable, glEnable, glGetIntegerv, glIsEnabled, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_WRAP_S, \
    GL_TEXTURE_WRAP_T)
from OpenGL.raw.GL.VERSION.GL_1_3 import GL_TEXTURE0, glActiveTexture


class GLTexture(IntEnum):
    """GL Draw Mode"""
    TEXTURE_2D = GL_TEXTURE_2D
    TEXTURE_MIN_FILTER = GL_TEXTURE_MIN_FILTER
    TEXTURE_MAG_FILTER = GL_TEXTURE_MAG_FILTER
    TEXTURE_WRAP_S = GL_TEXTURE_WRAP_S
    TEXTURE_WRAP_T = GL_TEXTURE_WRAP_T

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


def gl_active_texture0():
    glActiveTexture(GL_TEXTURE0)