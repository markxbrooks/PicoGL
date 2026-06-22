"""
Provides utility functions to create layout descriptors and attribute specifications
for vertex buffers using the picogl library.

The module includes functions to assist in defining layout descriptions
and generating vertex attribute configurations, such as element attributes
and common attributes with position and color specifications. These configurations
are primarily intended for use with OpenGL-based rendering.

Functions:
- create_layout: Generates a layout descriptor using the provided attributes.
- create_element_attributes: Returns a predefined set of element attribute specifications
  with position data.
- create_common_attributes: Returns a predefined set of vertex attribute specifications
  with both position and color data.
"""

from picogl.buffers.attributes import (
    LayoutDescriptor,
    legacy_attribute_spec,
)
from picogl.gpu.buffers.vertex.aliases import VertexBufferRole
from picogl.core.enums.numerical import GLNumeric


def create_layout(attributes):
    return LayoutDescriptor(attributes=attributes)


def create_element_attributes():
    return [
        legacy_attribute_spec(
            VertexBufferRole.VBO,
            0,
            name="positions",
            type=GLNumeric.FLOAT,
        )
    ]


def create_common_attributes():
    return [
        legacy_attribute_spec(
            VertexBufferRole.VBO,
            0,
            name="positions",
            type=GLNumeric.FLOAT,
        ),
        legacy_attribute_spec(
            VertexBufferRole.CBO,
            1,
            name="colors",
            type=GLNumeric.FLOAT,
        ),
    ]
