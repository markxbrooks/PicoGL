"""
Defines enumerations for legacy OpenGL primitive types.

This module contains an enumeration class that maps OpenGL constants to
specific primitive types, which were deprecated in later versions of OpenGL.
It can help when working with older OpenGL code or transitioning legacy
implementations to newer OpenGL versions.
"""
from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POLYGON
from OpenGL.raw.GL.VERSION.GL_4_0 import GL_QUADS


class GLLegacyPrimitive(IntEnum):
    """Deprecate the GLDramMode versions"""

    QUADS = GL_QUADS
    POLYGON = GL_POLYGON