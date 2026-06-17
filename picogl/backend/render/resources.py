"""Frame-scoped GPU resource descriptors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Texture:
    """GPU texture node in a render graph."""

    name: str
    width: int
    height: int
    format: int
    handle: Optional[int] = None


@dataclass
class RenderTarget:
    """Color/depth render target."""

    name: str
    color: Texture
    depth: Optional[Texture] = None


class FrameResources:
    """Allocator for per-frame transient GPU resources."""

    def __init__(self):
        self.textures: dict[str, Texture] = {}
        self.render_targets: dict[str, RenderTarget] = {}

    def create_texture(self, name: str, width: int, height: int, fmt: int) -> Texture:
        tex = Texture(name, width, height, fmt)
        self.textures[name] = tex
        return tex

    def create_render_target(
        self,
        name: str,
        color: Texture,
        depth: Optional[Texture] = None,
    ) -> RenderTarget:
        target = RenderTarget(name, color, depth)
        self.render_targets[name] = target
        return target
