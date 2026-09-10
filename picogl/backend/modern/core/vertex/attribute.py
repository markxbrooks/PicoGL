"""
Provides a representation of a single vertex attribute slot for the build_vao function.

This class is used to define and encapsulate a vertex attribute, including its index,
associated data, and its corresponding name, which is represented as a VBOType.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from picogl.gpu.buffers.vertex.vbo import VBOType


@dataclass(frozen=True)
class VertexAttribute:
    """One vertex attribute slot for :func:`build_vao`."""

    index: int
    data: np.ndarray
    name: VBOType
