"""Ordered render-pass execution (no dependency resolution)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from picogl.backend.render.pass_ import RenderPass

if TYPE_CHECKING:
    from picogl.backend.gl.backend import GLBackend


class RenderPipeline:
    """Execute render passes in registration order."""

    def __init__(self):
        self.passes: list[RenderPass] = []

    def add(self, render_pass: RenderPass) -> None:
        self.passes.append(render_pass)

    def execute(self, backend: "GLBackend") -> None:
        for render_pass in self.passes:
            render_pass.execute(backend)
