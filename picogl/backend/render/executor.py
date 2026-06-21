"""Render graph executor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from picogl.backend.render.graph import DependencyGraph, RenderGraph, topo_sort

if TYPE_CHECKING:
    from picogl.backend.gl.backend import GLBackend


class RenderGraphExecutor:
    """Resolve pass order and execute through a gl backend."""

    def __init__(self, backend: "GLBackend"):
        self.backend = backend

    def execute(self, graph: RenderGraph) -> None:
        dep = DependencyGraph()
        dep.build(graph.passes)

        order = topo_sort([p.name for p in graph.passes], dep.edges)
        lookup = {p.name: p for p in graph.passes}

        for name in order:
            render_pass = lookup[name]
            render_pass.execute(self.backend)
