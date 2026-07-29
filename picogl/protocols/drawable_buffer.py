"""
OpenGL buffer protocols for ElMo.

Defines a shared interface (DrawableBuffer) for buffer/VAO objects used in
legacy and modern backends, so group-level and draw code can treat them
uniformly.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol, TypeAlias, runtime_checkable

import numpy as np


@runtime_checkable
class DrawableBuffer(Protocol):
    """
    Protocol for OpenGL buffer/VAO objects that can be bound, drawn, and deleted.

    Implementors must provide bind(), unbind(), draw(), and delete().
    Optional: is_valid() for validity checks; __enter__/__exit__ for
    context-manager support (with obj: obj.draw()).

    Legacy VBO groups and modern VAOs (AtomVAO, BondsVAO, RibbonVAO, CalphasVAO,
    RibbonVBG, etc.) conform to this protocol.
    """

    def bind(self) -> None:
        """Bind this buffer/VAO for rendering."""
        ...

    def unbind(self) -> None:
        """Unbind this buffer/VAO after rendering."""
        ...

    def draw(self, *args: Any, **kwargs: Any) -> None:
        """Issue draw calls. Signature is backend-specific (e.g. atom_count, index_count)."""
        ...

    def delete(self) -> None:
        """Release GPU resources."""
        ...

    def data_length(self) -> int:
        """Number of vertices (or drawable elements) in this buffer."""
        ...


@runtime_checkable
class VertexBufferDataSource(Protocol):
    """Single legacy/modern VBO or EBO with CPU-side ``data``."""

    data: np.ndarray | None


@runtime_checkable
class BufferContainer(Protocol):
    """Wrapper or group holding nested VAO/VBO handles (e.g. ElMo buffer groups)."""

    vao: DrawableBuffer | int | None
    vbo: VertexBufferDataSource | int | None
    named_vbos: Mapping[Any, VertexBufferDataSource]
    index_count: int


DrawableLengthInput: TypeAlias = (
    DrawableBuffer | BufferContainer | VertexBufferDataSource | None
)
