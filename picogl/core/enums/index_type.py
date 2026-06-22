"""
Provides definitions for index types used in OpenGL rendering.

This module defines an enumeration representing different OpenGL index
types. These index types are used to specify the data type of indices in
element array buffers during OpenGL rendering operations.
"""

from enum import IntEnum

from OpenGL.raw.GL._types import GL_UNSIGNED_INT, GL_UNSIGNED_SHORT


class GLIndexType(IntEnum):
    """Index type"""
    UNSIGNED_INT = GL_UNSIGNED_INT
    UNSIGNED_SHORT = GL_UNSIGNED_SHORT
