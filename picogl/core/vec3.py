"""Four-component vector value object."""

from dataclasses import dataclass

from picogl.core.mixin.vec3 import Vec3Mixin


@dataclass(frozen=True)
class Vec3(Vec3Mixin):
    """A four-component vector, including homogeneous coordinates."""

    x: float
    y: float
    z: float

    def to_tuple(self) -> tuple[float, float, float]:
        """Return the vector components as a tuple."""
        return self.x, self.y, self.z
