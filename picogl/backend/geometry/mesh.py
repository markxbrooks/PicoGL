"""GPU-resident mesh abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GPUMesh(ABC):
    """Uploaded or CPU-bound geometry ready for bind + draw."""

    @abstractmethod
    def bind(self) -> None:
        """Bind GPU buffers or client arrays for drawing."""

    @abstractmethod
    def draw(self, mode: int) -> None:
        """Issue draw calls for the bound mesh."""

    def unbind(self) -> None:
        """Release binding after draw (optional)."""

    def delete(self) -> None:
        """Release GPU resources (optional)."""
