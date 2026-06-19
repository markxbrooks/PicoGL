"""
Create layouts for VOAs and VBGs
"""

from picogl.buffers.attributes import (
    AttributeSpec,
    LayoutDescriptor,
    legacy_attribute_spec,
)
from picogl.buffers.vertex.aliases import VertexBufferRole
from picogl.state.draw_mode import GLDataType


def create_layout(attributes):
    return LayoutDescriptor(attributes=attributes)


def create_element_attributes():
    return [
        legacy_attribute_spec(
            VertexBufferRole.VBO,
            0,
            name="positions",
            type=GLDataType.FLOAT,
        )
    ]


def create_common_attributes():
    return [
        legacy_attribute_spec(
            VertexBufferRole.VBO,
            0,
            name="positions",
            type=GLDataType.FLOAT,
        ),
        legacy_attribute_spec(
            VertexBufferRole.CBO,
            1,
            name="colors",
            type=GLDataType.FLOAT,
        ),
    ]
