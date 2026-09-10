import numpy as np
from pyrr import Matrix44

from picogl.core.camera import FOVY, ProjectionConfig


def calculate_projection_matrix(width: int, height: int) -> Matrix44:
    """
    calculate_projection_matrix

    :param width: int
    :param height: int
    :return: Matrix44
    """
    aspect = width / height if height != 0 else 1
    return Matrix44.perspective_projection(
        fovy=FOVY,
        aspect=aspect,
        near=ProjectionConfig.near,
        far=ProjectionConfig.far,
    ).astype(np.float32)
