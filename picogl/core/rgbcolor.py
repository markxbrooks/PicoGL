"""
RGB Color

Simple, readable structure using dataclasses.
Default values give you a convenient “white opaque” color (1.0, 1.0, 1.0, 1.0).
RGBA correctly inherits from RGB, reusing its fields.


Type hints and value constraints**: Ensure color components are in the [0.0, 1.0] range and handle possible out-of-range values.
  You could add a post-init check to enforce bounds.
Immutability (optional)**: If colors shouldn’t change after creation, consider making the dataclasses frozen.
Validation utility**: Provide a small helper to clamp values or validate inputs.
String representation**: Customize repr for clearer debugging, especially for RGBA.
Interoperability**: If you plan to convert to/from common formats (tuples, lists, hex), consider adding convenience methods.

"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
import numpy as np

# Utility
def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def as_vec3_array(data) -> np.ndarray:
    """as vec3 array"""
    return np.asarray(data, dtype=np.float32).reshape(-1, 3)

# Vec3 mixin to share common RGB-like behavior
class Vec3Mixin:
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

# RGBColor
@dataclass
class RGBColor(Vec3Mixin):
    """RGB color"""
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0

    def __post_init__(self):
        # Enforce constraints on init
        self.r = clamp01(self.r)
        self.g = clamp01(self.g)
        self.b = clamp01(self.b)

    def to_tuple(self) -> Tuple[float, float, float]:
        return self.r, self.g, self.b

    @property
    def alpha(self) -> float:
        return 1.0

    @classmethod
    def from_rgba_tuple(cls, t: Tuple[float, float, float, float]):
        r, g, b, _a = t
        return cls(r, g, b)

    def with_alpha(self, alpha: float) -> "RGBAColor":
        return RGBAColor(self.r, self.g, self.b, alpha)

# RGBAColor
@dataclass
class RGBAColor(RGBColor):
    """RGBA color"""
    a: float = 1.0

    def __post_init__(self):
        super().__post_init__()
        self.a = clamp01(self.a)

    def to_tuple(self) -> Tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)

    def without_alpha(self) -> RGBColor:
        return RGBColor(self.r, self.g, self.b)


def clamp01_old(x: float) -> float:
    return max(0.0, min(1.0, x))


@dataclass(frozen=False)
class RGBColorOld:
    """RGB color"""

    r: float = 1.0
    g: float = 1.0
    b: float = 1.0

    def __post_init__(self):
        setattr(self, "r", clamp01(self.r))
        setattr(self, "g", clamp01(self.g))
        setattr(self, "b", clamp01(self.b))

    @property
    def tuple(self) -> tuple[float, float, float]:
        return self.to_tuple()

    def to_tuple(self) -> tuple[float, float, float]:
        return self.r, self.g, self.b

    def with_alpha(self, alpha: float) -> "RGBAColor":
        return RGBAColor(self.r, self.g, self.b, alpha)


@dataclass(frozen=False)
class RGBAColorOld(RGBColor):
    """RGBA color"""

    a: float = 1.0

    def __post_init__(self):
        super().__post_init__()
        setattr(self, "a", clamp01(self.a))

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (*super().to_tuple(), self.a)

    def without_alpha(self) -> "RGBColor":
        return RGBColor(self.r, self.g, self.b)
