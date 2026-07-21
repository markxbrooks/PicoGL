"""Sphere geometry helpers (pure math, no OpenGL)."""

from __future__ import annotations

import math
from collections.abc import Iterator

from picogl.core.vec3 import Vec3


def iter_longitudes(slices: int) -> Iterator[float]:
    """Yield longitude angles for each slice (including closure vertex)."""
    for j in range(slices + 1):
        yield 2 * math.pi * j / slices


def latitude_for_stack(stack: int, stacks: int) -> float:
    """Latitude in radians for stack index ``stack`` in ``[0, stacks]``."""
    return math.pi * (-0.5 + stack / stacks)


def generate_ring(radius: float, latitude: float, slices: int) -> list[Vec3]:
    """Vertices on one latitude circle of a sphere centered at the origin."""
    return [
        Vec3.sphere(radius, latitude, lng)
        for lng in iter_longitudes(slices)
    ]
