"""
Provides utilities and context managers for managing OpenGL textures.

This module defines enumerations and helper classes for texture handling, along
with context managers for safely enabling and binding textures in an OpenGL
environment. It aims to simplify texture management tasks and ensure proper
state restoration after operations.
"""

from contextlib import contextmanager
from dataclasses import dataclass

from OpenGL.GL import (glBindTexture,
                       glDisable, glEnable, glGetIntegerv, glIsEnabled)

from picogl.state.param import GLParam
from picogl.state.query import GLStateQuery
from picogl.texture.gltexture import GLTexture


@dataclass(frozen=True)
class TexCoord2f:
    u: float
    v: float


@contextmanager
def texture2d_legacy_manager():
    """texture legacy manager"""
    was_enabled = glIsEnabled(GLTexture.TEXTURE_2D)
    previous_binding = glGetIntegerv(GLTexture.TEXTURE_BINDING_2D)

    try:
        if not was_enabled:
            glEnable(GLTexture.TEXTURE_2D)
        yield
    finally:
        glBindTexture(GLTexture.TEXTURE_2D, previous_binding)
        if not was_enabled:
            glDisable(GLTexture.TEXTURE_2D)


@contextmanager
def bound_texture(texture_id: int, unit: int = GLTexture.TEXTURE0):
    """
    Bind a texture to a specific unit, restoring previous state.

    Guarantees:
    - Active texture unit restored
    - Previous binding for that unit restored
    """

    # Save current active unit (returns GL_TEXTUREi enum)
    # prev_active = glGetIntegerv(GLTexture.ACTIVE_TEXTURE)
    state = GLStateQuery()

    prev_active = state.get(GLParam.ACTIVE_TEXTURE)
    prev_binding = state.get(GLParam.TEXTURE_BINDING_2D)

    try:
        # Switch to requested unit
        GLTexture.set_active(unit)

        # Save binding for THIS unit
        # prev_binding = glGetIntegerv(GLTexture.TEXTURE_BINDING_2D)

        # Bind new texture
        GLTexture.bind(GLTexture.TEXTURE_2D, texture_id or 0)

        yield

    finally:
        # Restore binding on the same unit
        GLTexture.bind(GLTexture.TEXTURE_2D, prev_binding)

        # Restore previously active unit
        GLTexture.set_active(prev_active)