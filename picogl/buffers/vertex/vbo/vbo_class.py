"""
A module for defining and managing vertex buffer object (VBO) types, mesh data
attributes, and their layout configurations.

This module provides enumerations for various VBO types and mesh data
attributes. It also includes functionality to compute the stride for attributes
based on predefined layouts and the shape of data.

Classes:
- VBOType: Enumeration for VBO types such as VBO, CBO, NBO, etc.
- MeshDataAttrs: Enumeration for mesh-related data attributes, e.g., vertices,
  colors, normals.

Constants:
- ATTRIBUTE_LAYOUT: A dictionary mapping VBO types to their associated attribute
  layouts, where predefined strides are provided or set to dynamic if specified
  as None.
"""

from picogl.utils.strenum import StrEnum


class VBOType(StrEnum):
    """VBO Type"""

    VBO = "vbo"
    CBO = "cbo"
    NBO = "nbo"
    EBO = "ebo"
    UVS = "uvs"


class MeshDataAttrs(StrEnum):
    """Mesh Data Attrs"""

    VERTICES = "vertices"
    COLORS = "colors"
    NORMALS = "normals"
    INDICES = "indices"
    TEXCOORDS = "texcoords"


ATTRIBUTE_LAYOUT = {
    VBOType.VBO: 3,
    VBOType.NBO: 3,
    VBOType.CBO: None,  # dynamic
}


def get_stride(attr, data):
    if ATTRIBUTE_LAYOUT[attr] is not None:
        return ATTRIBUTE_LAYOUT[attr]
    return data.shape[1]
