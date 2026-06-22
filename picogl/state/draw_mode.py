"""
This module defines enumeration classes mapping various OpenGL constants
to more easily readable and manageable Python enumerations. These enums
facilitate interactions with OpenGL by providing structured and semantically
meaningful groupings for matrix modes, clip planes, bit masks, data types,
usage hints, buffer targets, and draw primitives.

Each enumeration corresponds to a specific set of OpenGL constants and can
be directly utilized when working with OpenGL APIs.
"""

from enum import IntEnum

from OpenGL.GL import (
    GL_DYNAMIC_DRAW,
    GL_ELEMENT_ARRAY_BUFFER,
    GL_LINE_LOOP,
    GL_LINE_STRIP,
    GL_LINE_STRIP_ADJACENCY,
    GL_LINES,
    GL_LINES_ADJACENCY,
    GL_PATCHES,
    GL_POLYGON,
    GL_QUAD_STRIP,
    GL_QUADS,
    GL_SHADER_STORAGE_BUFFER,
    GL_STATIC_DRAW,
    GL_TRIANGLE_STRIP,
    GL_TRIANGLE_STRIP_ADJACENCY,
    GL_TRIANGLES,
    GL_TRIANGLES_ADJACENCY,
    GL_UNIFORM_BUFFER,
    GL_UNSIGNED_INT,
    GL_UNSIGNED_SHORT,
)
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POINTS
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_ARRAY_BUFFER


class GLIndexType(IntEnum):
    UNSIGNED_INT = GL_UNSIGNED_INT
    UNSIGNED_SHORT = GL_UNSIGNED_SHORT


class GLUsageHint(IntEnum):
    """Usage Hint"""

    STATIC_DRAW = GL_STATIC_DRAW
    DYNAMIC_DRAW = GL_DYNAMIC_DRAW


class GLBufferTarget(IntEnum):
    """gl Buffer Target"""

    ARRAY = GL_ARRAY_BUFFER
    ELEMENT = GL_ELEMENT_ARRAY_BUFFER
    UNIFORM = GL_UNIFORM_BUFFER
    SHADER_STORAGE = GL_SHADER_STORAGE_BUFFER


class GLLegacyPrimitive(IntEnum):
    """Deprecate the GLDramMode versions"""

    QUADS = GL_QUADS
    POLYGON = GL_POLYGON


class GLDrawMode(IntEnum):
    """gl Draw Mode"""

    QUAD_STRIP = GL_QUAD_STRIP
    TRIANGLE_STRIP = GL_TRIANGLE_STRIP
    TRIANGLES = GL_TRIANGLES
    POINTS = GL_POINTS
    LINE_STRIP = GL_LINE_STRIP
    QUADS = GL_QUADS
    POLYGON = GL_POLYGON
    LINES = GL_LINES
    LINE_LOOP = GL_LINE_LOOP
    LINE_STRIP_ADJACENCY = GL_LINE_STRIP_ADJACENCY
    LINES_ADJACENCY = GL_LINES_ADJACENCY
    TRIANGLE_STRIP_ADJACENCY = GL_TRIANGLE_STRIP_ADJACENCY
    TRIANGLES_ADJACENCY = GL_TRIANGLES_ADJACENCY
    PATCHES = GL_PATCHES

    @classmethod
    def choices(cls):
        return [m.value for m in cls]
