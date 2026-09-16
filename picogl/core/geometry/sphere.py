"""Sphere geometry helpers (pure math, no OpenGL)."""

from __future__ import annotations

import math
from collections.abc import Iterator

import numpy as np

from picogl.core.vec3 import Vec3
from picogl.renderer.mesh_arrays import MeshArrays


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
) -> MeshArrays:
    """Build a unit-sphere triangle mesh centered at the origin.

    This is a geometry producer only: it does not instance, color, or batch
    spheres.

    :param radius: Sphere radius
    :param slices: Longitudinal subdivisions
    :param stacks: Latitudinal subdivisions
    :return: :class:`~picogl.renderer.mesh_arrays.MeshArrays` with origin-centered
        positions, normals, and triangle indices (no colors)
    """
    vertices: list[list[float]] = []
    normals: list[list[float]] = []
    indices: list[int] = []

    for stack in range(stacks + 1):
        lat = latitude_for_stack(stack, stacks)
        z = radius * math.sin(lat)
        zr = radius * math.cos(lat)

        for lng in iter_longitudes(slices):
            x = math.cos(lng) * zr
            y = math.sin(lng) * zr
            vertices.append([x, y, z])
            normals.append([x / radius, y / radius, z / radius])

    for stack in range(stacks):
        for j in range(slices):
            v1 = stack * (slices + 1) + j
            v2 = v1 + 1
            v3 = (stack + 1) * (slices + 1) + j
            v4 = v3 + 1
            indices.extend([v1, v2, v3])
            indices.extend([v2, v4, v3])

    return MeshArrays(
        positions=np.array(vertices, dtype=np.float32),
        normals=np.array(normals, dtype=np.float32),
        indices=np.array(indices, dtype=np.uint32),
    )
