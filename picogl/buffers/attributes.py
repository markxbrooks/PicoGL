"""
Attribute and layout specification handling module.

This module defines data structures for specifying attributes and layout
descriptors in a graphical or geometrical context. These structures are
used to describe how data is stored, accessed, and organized for rendering
or processing purposes.
"""

from dataclasses import dataclass
from typing import List


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


@dataclass
class LayoutDescriptor:
    """Layout descriptor."""
    attributes: List[AttributeSpec]
