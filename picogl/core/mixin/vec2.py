from __future__ import annotations

from typing import Tuple, ClassVar

import numpy as np


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


class Vec2Mixin:
    """Vec3 Mixin"""
    COMPONENTS: ClassVar[int] = 2

    def to_tuple(self) -> Tuple[float, float]:
        raise NotImplementedError

    @property
    def tuple(self) -> Tuple[float, float]:
        return self.to_tuple()

    @property
    def xyz(self) -> Tuple[float, float]:
        return self.to_tuple()

    def clamp(self) -> None:
        """Clamp components in-place if the class is mutable."""
        for name in self._component_names():
            setattr(self, name, clamp01(getattr(self, name)))
