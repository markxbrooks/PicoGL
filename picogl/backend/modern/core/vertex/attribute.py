"""
Provides a representation of a single vertex attribute slot for the build_vao function.

This class pairs an :class:`~picogl.gpu.buffers.attributes.AttributeSpec` (how the
attribute is represented) with the CPU array that will be uploaded.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from picogl.backend.gl.enums import GLNumeric
from picogl.gpu.buffers.attributes import AttributeSpec
from picogl.gpu.buffers.vertex.vbo import VBOType


@dataclass(frozen=True)
class VertexAttribute:
    """One vertex attribute slot for :func:`build_vao`.

    :param spec: Vertex attribute layout (index, size, dtype, semantic name).
    :param data: CPU vertex data uploaded into the corresponding VBO.
    """

    spec: AttributeSpec
    data: np.ndarray

    @classmethod
    def slot(
        cls,
        index: int,
        data: np.ndarray,
        name: VBOType | str,
        *,
        size: int | None = None,
        dtype: GLNumeric = GLNumeric.FLOAT,
    ) -> VertexAttribute:
        """Build a :class:`VertexAttribute` from an index, array, and semantic name.

        :param index: Vertex attribute location.
        :param data: CPU vertex data.
        :param name: Semantic buffer name (e.g. :class:`VBOType`).
        :param size: Components per vertex; inferred from ``data`` when omitted.
        :param dtype: OpenGL component type.
        :return: Attribute wrapping an :class:`AttributeSpec` and ``data``.
        """
        arr = np.asarray(data)
        if size is None:
            size = 3 if arr.ndim == 1 else int(arr.shape[-1])
        spec = AttributeSpec(
            name=name,
            index=index,
            size=size,
            dtype=dtype,
        )
        return cls(spec=spec, data=arr)
