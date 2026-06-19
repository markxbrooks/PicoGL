"""
Unproject
"""

from typing import Optional, Tuple

import numpy as np
from decologr import Decologr as log
from OpenGL.GL import glGetDoublev, glGetIntegerv
from OpenGL.GLU import gluUnProject
from OpenGL.raw.GL._types import GL_FLOAT
from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_DEPTH_COMPONENT,
    GL_MODELVIEW_MATRIX,
    GL_PROJECTION_MATRIX,
    GL_VIEWPORT,
    glFlush,
    glIsEnabled,
    glReadPixels,
)

from picogl.backend.capability import GLPipelineCapability


def unproject(x: int, y: int) -> Optional[Tuple[float, float, float]]:
    """
    unproject

    :param x: x coordinate
    :param y: y coordinate
    :return: Tuple[int, int, int] coordinate_data_main

    Un-projects screen coordinate_data_main (x, y) into 3D world coordinate_data_main.
    Assumes OpenGL context is current -Ensure OpenGL context is current if needed
    i.e. self.makeCurrent() ← must be called before this if in Qt widget
    """
    model_view = glGetDoublev(GL_MODELVIEW_MATRIX)
    log.parameter("model_view", model_view, silent=True)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    log.parameter("projection", projection, silent=True)
    viewport = glGetIntegerv(GL_VIEWPORT)
    log.parameter("viewport", viewport, silent=True)

    y_gl = viewport[3] - y
    log.parameter("y_gl", y_gl, silent=True)

    if not (0 <= x < viewport[2] and 0 <= y_gl < viewport[3]):
        log.message(f"Coordinates out of bounds: ({x}, {y_gl})")
        return None

    if not glIsEnabled(GLPipelineCapability.DEPTH_TEST):
        log.warning("Warning: GL_DEPTH_TEST is not enabled")

    # Read depth safely
    depth = np.array([0.0], dtype=np.float32)
    # log.parameter("depth", depth)
    try:
        glFlush()
        glReadPixels(x, y_gl, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, depth)
    except Exception as ex:
        log.error(f"glReadPixels failed: {ex}")
        return None

    wz = float(depth[0])
    if wz == 1.0:
        return None
    log.parameter("depth", depth, silent=True)
    wx, wy, wz = gluUnProject(x, y_gl, wz, model_view, projection, viewport)
    log.parameter("wx", wx, silent=True)
    log.parameter("wy", wy, silent=True)
    log.parameter("wz", wz, silent=True)
    return wx, wy, wz
