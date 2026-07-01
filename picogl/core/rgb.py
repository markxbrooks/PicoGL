"""
RGB Color 
"""


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

from dataclasses import dataclass

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

@dataclass(frozen=True)
class RGB:
    """RGB color"""
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0

    def post_init(self):
        object.setattr(self, 'r', clamp01(self.r))
        object.setattr(self, 'g', clamp01(self.g))
        object.setattr(self, 'b', clamp01(self.b))

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.r, self.g, self.b)

@dataclass(frozen=True)
class RGBA(RGB):
    """RGBA color"""
    a: float = 1.0

    def post_init(self):
        super().post_init()
        object.setattr(self, 'a', clamp01(self.a))

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)

If you don’t want immutability, drop frozen=True and adjust post_init accordingly.

If you share how you plan to use these classes (e.g., color conversions, rendering, serialization), I can tailor the tweaks to fit your context.
