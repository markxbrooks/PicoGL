"""Adapt existing DrawableBuffer implementors to GPUMesh."""

from __future__ import annotations

from typing import Any

from picogl.backend.geometry.mesh import GPUMesh


class DrawableBufferAdapter(GPUMesh):
    """Wrap a :class:`~picogl.protocols.drawable_buffer.DrawableBuffer` as GPUMesh."""

    def __init__(self, buffer: Any, draw_kwargs: dict | None = None):
        self._buffer = buffer
        self._draw_kwargs = draw_kwargs or {}

    def bind(self) -> None:
        self._buffer.bind()

    def unbind(self) -> None:
        self._buffer.unbind()

    def draw(self, mode: int) -> None:
        kwargs = dict(self._draw_kwargs)
        kwargs.setdefault("mode", mode)
        self._buffer.draw(**kwargs)

    def delete(self) -> None:
        self._buffer.delete()
