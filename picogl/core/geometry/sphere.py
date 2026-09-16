"""Sphere geometry helpers (pure math, no OpenGL)."""

from __future__ import annotations

import math
from collections.abc import Iterator
from dataclasses import dataclass

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


def sphere_mesh_np(
        radius: float = 1.0,
        slices: int = 16,
        stacks: int = 16,
) -> MeshArrays:
    """Build a sphere triangle mesh centered at the origin.

    This is a geometry producer only: it does not instance, color, or batch
    spheres.

    Parameters
    ----------
    radius
        Sphere radius.
    slices
        Longitudinal subdivisions.
    stacks
        Latitudinal subdivisions.

    Returns
    -------
    MeshArrays
        Origin-centered positions, normals, and triangle indices.
    """
    latitudes = np.linspace(
        -np.pi / 2,
        np.pi / 2,
        stacks + 1,
        dtype=np.float32,
    )

    longitudes = np.linspace(
        0.0,
        2.0 * np.pi,
        slices + 1,
        dtype=np.float32,
    )

    lat, lng = np.meshgrid(latitudes, longitudes, indexing="ij")

    cos_lat = np.cos(lat)
    sin_lat = np.sin(lat)
    cos_lng = np.cos(lng)
    sin_lng = np.sin(lng)

    positions = generate_positions(cos_lat, cos_lng, radius, sin_lat, sin_lng)

    normals = generate_normals(cos_lat, cos_lng, sin_lat, sin_lng)

    row = np.arange(stacks, dtype=np.uint32)[:, None]
    col = np.arange(slices, dtype=np.uint32)[None, :]

    stride = slices + 1

    v1 = row * stride + col
    v2 = v1 + 1
    v3 = v1 + stride
    v4 = v3 + 1

    indices = generate_indices(v1, v2, v3, v4)

    return MeshArrays(
        positions=positions.astype(np.float32, copy=False),
        normals=normals.astype(np.float32, copy=False),
        indices=indices,
    )


def generate_indices(v1: ndarray[Any, dtype[unsignedinteger[Any]]] | Any, v2: int | Any, v3: int | Any,
                     v4: int | Any) -> ndarray[Any, dtype[Any]]:
    indices = np.stack(
        (
            v1,
            v2,
            v3,
            v2,
            v4,
            v3,
        ),
        axis=-1,
    ).reshape(-1)
    return indices


def generate_normals(cos_lat, cos_lng, sin_lat, sin_lng) -> ndarray[Any, dtype[Any]]:
    normals = np.stack(
        (
            cos_lat * cos_lng,
            cos_lat * sin_lng,
            sin_lat,
        ),
        axis=-1,
    ).reshape(-1, 3)
    return normals


def generate_positions(cos_lat, cos_lng, radius: float, sin_lat, sin_lng) -> ndarray[Any, dtype[Any]]:
    positions = np.stack(
        (
            radius * cos_lat * cos_lng,
            radius * cos_lat * sin_lng,
            radius * sin_lat,
        ),
        axis=-1,
    ).reshape(-1, 3)
    return positions


def sphere_mesh_python(
        radius: float = 1.0,
        slices: int = 16,
        stacks: int = 16,
) -> MeshArrays:
    """Build a sphere triangle mesh centered at the origin.

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


@dataclass(frozen=True, slots=True)
class SphereGeometrySpec:
    """Parameters controlling sphere mesh generation.

    This is configuration only: it does not build geometry. Pass an instance
    to :class:`SphereMesh`.
    """

    radius: float = 1.0
    slices: int = 16
    stacks: int = 16


class SphereMesh:
    """Build origin-centered sphere geometry from a :class:`SphereGeometrySpec`.

    Derived vertex and index counts live here so the spec stays parameters
    only. :meth:`build` returns colorless :class:`~picogl.renderer.mesh_arrays.MeshArrays`.
    """

    def __init__(self, spec: SphereGeometrySpec) -> None:
        self.spec = spec

    @property
    def vertices_per_item(self) -> int:
        """Number of vertices in one sphere instance."""
        return (self.spec.stacks + 1) * (self.spec.slices + 1)

    @property
    def elements_per_item(self) -> int:
        """Number of triangle indices in one sphere instance."""
        return 6 * self.spec.stacks * self.spec.slices

    def build(self) -> MeshArrays:
        """Build a sphere template centered at the origin.

        :return: Positions, normals, and indices with no colors
        """
        return sphere_mesh(
            radius=self.spec.radius,
            slices=self.spec.slices,
            stacks=self.spec.stacks,
        )


# Use Numpy or python loops for Sphere generation
# sphere_mesh = sphere_mesh_python

sphere_mesh = sphere_mesh_np
