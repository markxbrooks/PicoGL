"""
Module for representing and managing OpenGL capabilities, fixed-function states, material
properties, and blend functions.

This module provides a collection of enumerations and data classes to facilitate the
representation of OpenGL states such as pipeline capabilities, blend factors, and material
properties. The module includes mappings between the defined enums and their OpenGL
integer constants for easy usage in OpenGL-related operations.
"""

from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_ALWAYS,
    GL_EQUAL,
    GL_GEQUAL,
    GL_GREATER,
    GL_LEQUAL,
    GL_LESS,
    GL_NEVER,
)


class GLDepthFunc(IntEnum):
    """GL Depth Comparison Function"""

    BLEND = GL_NEVER
    LESS = GL_LESS
    EQUAL = GL_EQUAL
    LEQUAL = GL_LEQUAL
    GREATER = GL_GREATER
    GEQUAL = GL_GEQUAL
    ALWAYS = GL_ALWAYS
