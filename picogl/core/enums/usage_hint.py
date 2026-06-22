"""
This module defines an enumeration for OpenGL usage hints and their corresponding
constants. It provides a type-safe way to specify intended usage patterns for OpenGL
buffer objects by mapping to GL constants.

The module exports the GLUsageHint Enum which includes static and dynamic draw hints
used in OpenGL for defining usage patterns.

"""
from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_5 import GL_STATIC_DRAW, GL_DYNAMIC_DRAW


class GLUsageHint(IntEnum):
    """Usage Hint"""

    STATIC_DRAW = GL_STATIC_DRAW
    DYNAMIC_DRAW = GL_DYNAMIC_DRAW