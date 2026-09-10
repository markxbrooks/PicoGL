"""
A function to construct a VertexArrayObject by populating it with vertex
attributes and optional index data.

This function initializes a VertexArrayObject using the provided vertex
attributes and optionally binds an index buffer for element-based rendering.
It encapsulates the setup of GPU-based vertex data into the given VertexArrayObject.

Attributes:
    vao (VertexArrayObject): The VertexArrayObject instance to be populated.
    attributes (list[VertexAttribute]): A list of VertexAttribute instances
        that define vertex data and layout for the VertexArrayObject.
    indices (np.ndarray | None): Optional array of indices to be used for index
        buffer binding. If None, index buffer is not populated.

Returns:
    VertexArrayObject: The updated VertexArrayObject containing the provided
    attributes and optional index data.
"""

from __future__ import annotations

import numpy as np

from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.backend.modern.core.vertex.attribute import VertexAttribute


def build_vao(
    vao: VertexArrayObject,
    attributes: list[VertexAttribute],
    indices: np.ndarray | None = None,
) -> VertexArrayObject:
    """Populate *vao* from attribute arrays and an optional element buffer."""
    vao.build(attributes=attributes, indices=indices)
    return vao
