"""
Create layouts for VOAs and VBGs
"""

from OpenGL.raw.GL._types import GL_FLOAT

from picogl.buffers.attributes import AttributeSpec, LayoutDescriptor


def create_layout(attributes):
    return LayoutDescriptor(attributes=attributes)


def create_element_attributes():
    return [
        AttributeSpec(
            name="positions",
            index=0,
            size=3,
            type=GL_FLOAT,
            normalized=False,
            stride=0,
            offset=0,
        )
    ]


def create_common_attributes():
    return [
        AttributeSpec(
            name="positions",
            index=0,
            size=3,
            type=GL_FLOAT,
            normalized=False,
            stride=0,
            offset=0,
        ),
        AttributeSpec(
            name="colors",
            index=1,
            size=3,
            type=GL_FLOAT,
            normalized=False,
            stride=0,
            offset=0,
        ),
    ]
