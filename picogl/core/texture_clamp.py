"""
This module provides functionality for handling OpenGL texture clamping constants
and related operations. It includes the `GLTextureClamp` class containing clamping
constants that can be used in texture operations.

Classes:
- GLTextureClamp: Represents OpenGL texture clamping constants.
"""

from OpenGL.raw.GL.VERSION.GL_1_2 import GL_CLAMP_TO_EDGE, GL_CLAMP_TO_BORDER


class GLTextureClamp:
    """gl Texture Clamping Constants."""
    TO_EDGE = GL_CLAMP_TO_EDGE
    TO_BORDER = GL_CLAMP_TO_BORDER
