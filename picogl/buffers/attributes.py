"""
Attribute and layout specification handling module.

This module defines data structures for specifying attributes and layout
descriptors in a graphical or geometrical context. These structures are
used to describe how data is stored, accessed, and organized for rendering
or processing purposes.
"""

from dataclasses import dataclass
from typing import List

import numpy as np
from picogl.buffers.vertex.vbo.vbo_class import VBOType


@dataclass
class AttributeSpec:
    """Attribute specification."""
    name: str  # semantic name ("positions", "colors", "normals", etc.)
    index: int  # attribute location
    size: int  # number of components (e.g., 3 for vec3)
    type: int  # GL_FLOAT, GL_INT, etc.
    normalized: bool
    stride: int
    offset: int  # in bytes
    vbo_type: VBOType = VBOType.VBO


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
