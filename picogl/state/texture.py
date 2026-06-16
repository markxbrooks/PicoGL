"""
Provides utilities and context managers for managing OpenGL textures.

This module defines enumerations and helper classes for texture handling, along
with context managers for safely enabling and binding textures in an OpenGL
environment. It aims to simplify texture management tasks and ensure proper
state restoration after operations.
"""

from contextlib import contextmanager
from dataclasses import dataclass

from OpenGL.GL import glDisable, glEnable, glIsEnabled

from picogl.texture.gltexture import GLTexture


@dataclass(frozen=True)
class TexCoord2f:
    """Tex Coord 2F"""

    u: float
    v: float


@dataclass(frozen=True)
class Vertex3f:
    """Vertex 3F"""

    x: float
    y: float
    z: float


@contextmanager
def texture2d_enabled():
    """Texture 2D Enabled"""
    was_enabled = glIsEnabled(GLTexture.TEXTURE_2D)
    try:
        if not was_enabled:
            glEnable(GLTexture.TEXTURE_2D)
        yield
    finally:
        if not was_enabled:
            glDisable(GLTexture.TEXTURE_2D)
