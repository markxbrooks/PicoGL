"""
Defines the CanonicalVertexAttrs class inheriting from StrEnum, representing
canonical attribute names for vertex data.

This class provides enumerated string constants for use in scenarios dealing
with vertex attributes such as positions, colors, normals, and indices.
"""

from picogl.utils.strenum import StrEnum


class CanonicalVertexAttrs(StrEnum):
    """Canonical Vertex Attrs"""

    POSITIONS = "positions"
    COLORS = "colors"
    NORMALS = "normals"
    INDICES = "indices"
