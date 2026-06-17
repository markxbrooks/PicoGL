"""Render pass primitive."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

from picogl.backend.state import RenderState

if TYPE_CHECKING:
    from picogl.backend.GL.backend import GLBackend
    from picogl.backend.render.resources import Texture


@dataclass
class RenderPass:
    """Declarative render pass with attached state and optional resource deps."""

    name: str
    state: RenderState
    execute_fn: Callable[[], None]
    reads: list["Texture"] = field(default_factory=list)
    writes: list["Texture"] = field(default_factory=list)

    def execute(self, backend: "GLBackend") -> None:
        backend.apply_state(self.state)
        self.execute_fn()
