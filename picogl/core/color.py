"""
Module to handle operations related to 3D texture upload.

This module provides functionality to upload 3D textures using
OpenGL, with proper texture parameters and normalization of the
input data.
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_RED, GL_RGB, GL_RGBA
from OpenGL.raw.GL.VERSION.GL_2_1 import GL_SRGB8


class GLColor:
    """gl Color"""

    RED = GL_RED
    RGBA = GL_RGBA
    RGB = GL_RGB
    SRGB8 = GL_SRGB8
