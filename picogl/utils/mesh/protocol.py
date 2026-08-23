"""Protocol for meshes uploaded and drawn by textured GLUT examples."""

from __future__ import annotations

from typing import Protocol


class MeshProtocol(Protocol):
    """Position + UV mesh with GPU upload and draw."""

    def upload(self) -> None: ...

    def draw(self) -> None: ...
