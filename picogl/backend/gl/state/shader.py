"""Scoped shader program binding."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Protocol


class _BindableShader(Protocol):
    def bind(self) -> object: ...

    def unbind(self) -> object: ...


@contextmanager
def gl_shader_bound(shader: _BindableShader) -> Iterator[None]:
    """Bind *shader* for the duration of the ``with`` block, then unbind."""
    shader.bind()
    try:
        yield
    finally:
        shader.unbind()
