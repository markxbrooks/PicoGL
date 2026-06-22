"""
Attribute and layout specification handling module.

This module defines data structures for specifying attributes and layout
descriptors in a graphical or geometrical context. These structures are
used to describe how data is stored, accessed, and organized for rendering
or processing purposes.
"""

from dataclasses import dataclass
from typing import List

from picogl.buffers.vertex.aliases import VertexBufferRole
from picogl.buffers.vertex.vbo.vbo_class import VBOType
from picogl.core.enums.numerical import GLNumeric


@dataclass
class AttributeSpec:
    """Attribute specification."""

    name: str  # semantic name ("positions", "colors", "normals", etc.)
    index: int  # attribute location
    size: int  # number of components (e.g., 3 for vec3)
    type: GLNumeric  # GL_FLOAT, GL_INT, etc.
    normalized: bool
    stride: int
    offset: int  # in bytes
    vbo_type: VBOType = VBOType.VBO
    role: VertexBufferRole = VertexBufferRole.VBO


def legacy_attribute_spec(
    role: VertexBufferRole,
    index: int,
    *,
    size: int = 3,
    name: str | VertexBufferRole | None = None,
    type: GLNumeric,
    normalized: bool = False,
    stride: int = 0,
    offset: int = 0,
) -> AttributeSpec:
    """Build an AttributeSpec with aligned legacy role, vbo_type, and name."""
    vbo_type = role.value if isinstance(role.value, VBOType) else VBOType(role.value)
    return AttributeSpec(
        name=name if name is not None else role,
        index=index,
        size=size,
        type=type,
        normalized=normalized,
        stride=stride,
        offset=offset,
        vbo_type=vbo_type,
        role=role,
    )


@dataclass
class LayoutDescriptor:
    """Layout descriptor."""

    attributes: List[AttributeSpec]
    _cache: dict[VBOType, AttributeSpec] | None = None

    def __getitem__(self, vbo_type: VBOType) -> AttributeSpec:
        try:
            return self.as_dict()[vbo_type]
        except KeyError:
            raise KeyError(f"{vbo_type} not defined in layout")

    def get_attr(self, vbo_type: VBOType) -> AttributeSpec:
        try:
            return self.as_dict()[vbo_type]
        except KeyError:
            raise KeyError(f"{vbo_type} not defined in layout")

    def has_attr(self, vbo_type: VBOType) -> bool:
        return vbo_type in self.as_dict()

    def as_dict(self) -> dict[VBOType, AttributeSpec]:
        if self._cache is None:
            self._cache = {attr.vbo_type: attr for attr in self.attributes}
        return self._cache

    @property
    def attr_dict(self) -> dict[VBOType, AttributeSpec]:
        """dict"""
        return self.as_dict()
