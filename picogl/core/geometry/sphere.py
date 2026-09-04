"""Sphere geometry helpers (pure math, no OpenGL)."""

from __future__ import annotations

import math
from collections.abc import Iterator

import numpy as np
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
    return [Vec3.sphere(radius, latitude, lng) for lng in iter_longitudes(slices)]


def unit_sphere_mesh(
    radius: float = 1.0,
    slices: int = 16,
    stacks: int = 16,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build a unit-sphere triangle mesh centered at the origin.

    Parameters
    ----------
    radius :
        Sphere radius.
    slices :
        Longitudinal subdivisions.
    stacks :
        Latitudinal subdivisions.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        ``(vertices, normals, indices)`` as float32/int32 arrays suitable for
        instancing at atom positions.
    """
    vertices: list[list[float]] = []
    normals: list[list[float]] = []

    for stack in range(stacks + 1):
        lat = latitude_for_stack(stack, stacks)
        z = radius * math.sin(lat)
        zr = radius * math.cos(lat)

        for lng in iter_longitudes(slices):
            x = math.cos(lng) * zr
            y = math.sin(lng) * zr
            vertices.append([x, y, z])
            normals.append([x / radius, y / radius, z / radius])

    indices: list[int] = []
    for stack in range(stacks):
        for j in range(slices):
            v1 = stack * (slices + 1) + j
            v2 = v1 + 1
            v3 = (stack + 1) * (slices + 1) + j
            v4 = v3 + 1
            indices.extend([v1, v2, v3])
            indices.extend([v2, v4, v3])

    return (
        np.array(vertices, dtype=np.float32),
        np.array(normals, dtype=np.float32),
        np.array(indices, dtype=np.uint32),
    )
