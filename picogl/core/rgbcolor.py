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
from typing import ClassVar, Tuple

from picogl.core.mixin.vec3 import Vec3Mixin, clamp01
from picogl.core.mixin.vec4 import Vec4Mixin
from typing_extensions import Self

# Utility

# Vec3 mixin to share common RGB-like behavior


# RGBColor
@dataclass(frozen=True)
class RGBColor(Vec3Mixin):
    """RGB color"""

    r: float = 1.0
    g: float = 1.0
    b: float = 1.0

    WHITE: ClassVar["Self"]
    BLACK: ClassVar["Self"]
    RED: ClassVar["Self"]
    GREEN: ClassVar["Self"]
    BLUE: ClassVar["Self"]
    BLUE_ISOSURFACE: ClassVar["Self"]
    YELLOW: ClassVar["Self"]
    MAGENTA: ClassVar["Self"]
    CYAN: ClassVar["Self"]

    def __post_init__(self):
        # Enforce constraints on init
        object.__setattr__(self, "r", clamp01(self.r))
        object.__setattr__(self, "g", clamp01(self.g))
        object.__setattr__(self, "b", clamp01(self.b))

    def to_tuple(self) -> Tuple[float, float, float]:
        return self.r, self.g, self.b

    @property
    def rgb(self) -> Tuple[float, float, float]:
        return self.r, self.g, self.b

    @property
    def alpha(self) -> float:
        return 1.0

    @classmethod
    def from_tuple(cls, rgb: Tuple[float, float, float]) -> RGBColor:
        return cls(*rgb)

    @classmethod
    def from_rgba_tuple(cls, t: Tuple[float, float, float, float]):
        r, g, b, _a = t
        return cls(r, g, b)

    def with_alpha(self, alpha: float) -> "RGBAColor":
        return RGBAColor(self.r, self.g, self.b, alpha)

    def scaled(self, factor: float) -> Self:
        return type(self)(
            self.r * factor,
            self.g * factor,
            self.b * factor,
        )


# RGBAColor
@dataclass(frozen=True)
class RGBAColor(RGBColor, Vec4Mixin):
    """RGBA color"""

    a: float = 1.0

    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, "a", clamp01(self.a))

    def to_tuple(self) -> Tuple[float, float, float, float]:
        return self.r, self.g, self.b, self.a

    @property
    def tuple(self) -> Tuple[float, float, float, float]:
        return self.to_tuple()

    def without_alpha(self) -> RGBColor:
        return RGBColor(self.r, self.g, self.b)

    def scaled(self, factor: float) -> Self:
        return type(self)(
            self.r * factor,
            self.g * factor,
            self.b * factor,
            self.a,
        )


_COLOR_VALUES = {
    "WHITE": (1.0, 1.0, 1.0),
    "BLACK": (0.0, 0.0, 0.0),
    "RED": (1.0, 0.0, 0.0),
    "GREEN": (0.0, 1.0, 0.0),
    "BLUE": (0.0, 0.0, 1.0),
    "BLUE_ISOSURFACE": (0.0, 0.0, 0.8),
    "YELLOW": (1.0, 1.0, 0.0),
    "MAGENTA": (1.0, 0.0, 1.0),
    "CYAN": (0.0, 1.0, 1.0),
}

for name, rgb in _COLOR_VALUES.items():
    setattr(RGBColor, name, RGBColor(*rgb))
    setattr(RGBAColor, name, RGBAColor(*rgb, 1.0))


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
