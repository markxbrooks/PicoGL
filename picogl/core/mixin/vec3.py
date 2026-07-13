from __future__ import annotations

from typing import Tuple

import numpy as np


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def as_vec3_array(data) -> np.ndarray:
    """as vec3 array"""
    return np.asarray(data, dtype=np.float32).reshape(-1, 3)


class Vec3Mixin:
    """Vec3 Mixin"""

    def to_tuple(self) -> Tuple[float, float, float]:
        raise NotImplementedError

    @property
    def tuple(self) -> Tuple[float, float, float]:
        return self.to_tuple()

    @property
    def xyz(self) -> Tuple[float, float, float]:
        return self.to_tuple()

    @classmethod
    def from_rgba_tuple(cls, t: Tuple[float, float, float, float]):
        raise NotImplementedError

    def clamp(self) -> None:
        """Clamp components in-place if the class is mutable."""
        for name in self._component_names():
            setattr(self, name, clamp01(getattr(self, name)))

    @classmethod
    def _component_names(cls):
        # helper for subclasses to declare their component names
        return ["r", "g", "b"]
