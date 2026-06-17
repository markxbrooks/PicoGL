"""Render graph and dependency resolution."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import TYPE_CHECKING

from picogl.backend.render.pass_ import RenderPass

if TYPE_CHECKING:
    pass


class RenderGraph:
    """Collection of render passes."""

    def __init__(self):
        self.passes: list[RenderPass] = []

    def add(self, render_pass: RenderPass) -> None:
        self.passes.append(render_pass)


class DependencyGraph:
    """Build pass ordering edges from resource read/write dependencies."""

    def __init__(self):
        self.edges: dict[str, set[str]] = defaultdict(set)

    def build(self, passes: list[RenderPass]) -> None:
        self.edges = defaultdict(set)
        for writer in passes:
            for reader in passes:
                if writer is reader:
                    continue
                if any(texture in reader.reads for texture in writer.writes):
                    self.edges[reader.name].add(writer.name)


def topo_sort(nodes: list[str], edges: dict[str, set[str]]) -> list[str]:
    """Topologically sort pass names; raise ValueError on cycles."""
    indeg: dict[str, int] = {name: 0 for name in nodes}
    adj: dict[str, list[str]] = defaultdict(list)

    for node, deps in edges.items():
        for dep in deps:
            if dep not in indeg:
                indeg[dep] = 0
            if node not in indeg:
                indeg[node] = 0
            adj[dep].append(node)
            indeg[node] += 1

    for name in nodes:
        indeg.setdefault(name, 0)

    queue = deque([name for name in nodes if indeg[name] == 0])
    result: list[str] = []

    while queue:
        name = queue.popleft()
        result.append(name)
        for nxt in adj[name]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)

    if len(result) != len(indeg):
        raise ValueError("render graph contains a dependency cycle")

    return result
