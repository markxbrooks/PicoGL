"""Provides functionality for representing spatial coordinates and a camera view in 3D space.

This module defines utility functions and protocols for transforming spatial data into
(x, y, z) tuples, as well as for setting up a camera view using OpenGL's gluLookAt function.
It includes support for Coordinates objects, 3-element sequences, and other objects with
x, y, and z attributes.
"""

from collections.abc import Sequence
from typing import Any, Protocol, Union

from molib.pdb.coordinate.coordinate import Coordinates
from OpenGL.raw.GLU import gluLookAt


class SupportsXYZ(Protocol):
    """Supports XYZ"""

    x: float
    y: float
    z: float


def _to_xyz(v: Coordinates | Sequence[float] | Any) -> tuple[float, float, float]:
    """Return *v* as an ``(x, y, z)`` tuple."""

    if isinstance(v, Coordinates):
        return v.x, v.y, v.z

    # Sequence-like (tuple, list, numpy array)
    try:
        x, y, z = v
        return float(x), float(y), float(z)
    except (TypeError, ValueError):
        pass

    # Object with x, y, z attributes
    if all(hasattr(v, attr) for attr in ("x", "y", "z")):
        return float(v.x), float(v.y), float(v.z)

    raise TypeError(
        "Expected Coordinates, a 3-element sequence, "
        "or an object with x, y and z attributes."
    )


def glu_look_at(
    eye_x: float,
    eye_y: float,
    eye_z: float,
    center_x: float,
    center_y: float,
    center_z: float,
    up_x: float,
    up_y: float,
    up_z: float,
) -> None:
    """glu lookat"""
    gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, up_x, up_y, up_z)


def glu_look_at_coords(
    eye: Union[Coordinates, Sequence[float], Any],
    center: Union[Coordinates, Sequence[float], Any],
    up: Union[Coordinates, Sequence[float], Any],
) -> None:
    """Preferred API: pass three Coordinates (or 3-element sequences / objects with x,y,z)."""
    ex, ey, ez = _to_xyz(eye)
    cx, cy, cz = _to_xyz(center)
    ux, uy, uz = _to_xyz(up)
    glu_look_at(ex, ey, ez, cx, cy, cz, ux, uy, uz)
