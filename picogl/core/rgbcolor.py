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

from picogl.core.mixin.vec3 import Vec3Mixin, clamp01

# Utility

# Vec3 mixin to share common RGB-like behavior


# RGBColor
@dataclass
class RGBColor(Vec3Mixin):
    """RGB color"""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __post_init__(self):
        # Enforce constraints on init
        self.x = clamp01(self.r)
        self.y = clamp01(self.g)
        self.z = clamp01(self.b)

    def to_tuple(self) -> Tuple[float, float, float]:
        return self.x, self.y, self.z


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
class Coord:
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
