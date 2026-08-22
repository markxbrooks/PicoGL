"""
OpenGL Matrix Retrieval Utility
===============================

This module provides a helper function to retrieve transformation matrices
from the OpenGL state machine. It uses `glGetFloatv` to query matrices such as
the modelview or projection matrix and returns them in a GLSL-compatible
format.
"""

from picogl.backend.legacy.core.camera.projection_state import (
    GLUProjectionState)
from picogl.core.camera import ProjectionConfig


def setup_matrices(
    aspect: float,
    fovy: float = ProjectionConfig.fovy,
    near: float = ProjectionConfig.near,
    far: float = ProjectionConfig.far,
):
    """
    setup_matrices

    :param aspect: float Aspect ratio
    :param fovy: Vertical field of view in degrees
    :param near: Near clipping plane
    :param far: Far clipping plane
    :return: None
    """
    GLUProjectionState().apply(
        ProjectionConfig(fovy=fovy, aspect=aspect, near=near, far=far)
    )
