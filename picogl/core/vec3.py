"""Three-component vector value object."""

from __future__ import annotations

import math
from dataclasses import dataclass

from picogl.core.mixin.vec3 import Vec3Mixin


@dataclass(frozen=True)
class Vec3(Vec3Mixin):
    """A three-component vector."""

    x: float
    y: float
    z: float

    def to_tuple(self) -> tuple[float, float, float]:
        """Return the vector components as a tuple."""
        return self.x, self.y, self.z

    def normalized(self) -> Vec3:
        """Return a unit-length copy of this vector.

        Near-zero length returns ``Vec3(0, 0, 0)``.
        """
        length = math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        if length < 1e-12:
            return Vec3(0.0, 0.0, 0.0)
        inv = 1.0 / length
        return Vec3(self.x * inv, self.y * inv, self.z * inv)

    @classmethod
    def sphere(cls, radius: float, lat: float, lng: float) -> Vec3:
        """Point on a sphere centered at the origin.

        ``lat`` is latitude in radians (``-pi/2`` at the south pole,
        ``+pi/2`` at the north pole). ``lng`` is longitude in radians.
        """
        cos_lat = math.cos(lat)
        return cls(
            radius * cos_lat * math.cos(lng),
            radius * cos_lat * math.sin(lng),
            radius * math.sin(lat),
        )
