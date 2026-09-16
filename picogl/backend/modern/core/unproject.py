"""
Modern OpenGL Unproject Function
"""

from typing import Any, Tuple

import glm
import numpy as np
from picogl.backend.modern.core.mvp import (
    convert_to_world_coordinates,
    create_normalized_device_vector,
    invert_mvp_matrix,
    normalize_device_coordinates,
)
from picogl.core.viewport import Viewport


def unproject(
    x: float, y: float, depth: float, inv_mvp: glm.mat4, viewport: Viewport | np.ndarray
) -> np.ndarray:
    """unproject"""
    if isinstance(viewport, Viewport):
        vx, vy, vw, vh = viewport.x, viewport.y, viewport.width, viewport.height
    else:
        vx, vy, vw, vh = (
            int(viewport[0]),
            int(viewport[1]),
            int(viewport[2]),
            int(viewport[3]),
        )

    y = vh - y

    ndc = np.array(
        [(x - vx) / vw * 2.0 - 1.0, (y - vy) / vh * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0],
        dtype=np.float32,
    )

    world = np.asarray(inv_mvp @ ndc, dtype=np.float32)

    w = world[3]
    if abs(w) < 1e-8:
        return None

    world = world / w
    return world[:3]


def unproject_test3(x, y, depth, inv_mvp, viewport):
    vx, vy, vw, vh = viewport

    # flip Y
    y = vh - y

    ndc = np.array(
        [(x - vx) / vw * 2.0 - 1.0, (y - vy) / vh * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0],
        dtype=np.float32,
    )
    world = np.asarray(inv_mvp @ ndc, dtype=np.float32)
    world = world / world[3]
    return world[:3]


def unproject_test(x, y, depth, inv_mvp, viewport, already_inverted=False):
    vx, vy, vw, vh = viewport

    y = vh - y

    ndc = np.array(
        [(x - vx) / vw * 2.0 - 1.0, (y - vy) / vh * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0],
        dtype=np.float32,
    )

    world = inv_mvp @ ndc

    if abs(world[3]) < 1e-8:
        return None

    world /= world[3]
    return world[:3]


def unproject_new(x, y, depth, model_view, projection, viewport):
    if depth >= 0.9999:
        return None

    vx, vy, vw, vh = viewport

    # Flip Y
    y = vh - y

    # Normalize to [-1, 1]
    ndc_x = (x - vx) / vw * 2.0 - 1.0
    ndc_y = (y - vy) / vh * 2.0 - 1.0
    ndc_z = depth * 2.0 - 1.0

    ndc = np.array([ndc_x, ndc_y, ndc_z, 1.0], dtype=np.float32)

    mvp = projection @ model_view
    inv_mvp = np.linalg.inv(mvp)

    world = inv_mvp @ ndc

    if abs(world[3]) < 1e-8:
        return None

    world /= world[3]
    return world[:3]
