"""Four-component vector value object."""

from dataclasses import dataclass

from picogl.core.mixin.vec4 import Vec4Mixin


@dataclass(frozen=True)
class Vec4(Vec4Mixin):
    """A four-component vector, including homogeneous coordinates."""

    x: float
    y: float
    z: float
    w: float = 1.0

    def to_tuple(self) -> tuple[float, float, float, float]:
        """Return the vector components as a tuple."""
        return self.x, self.y, self.z, self.w
