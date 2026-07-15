"""
Set up model_matrix view projection (MVP) matrix for 3D rendering.

    This function constructs a combined projection and view matrix based on camera orbit angles,
    zoom level, and viewport aspect ratio. It simulates a camera orbiting around the origin
    and returns a 4x4 transformation matrix suitable for use in OpenGL shaders.


    :Example:

    .. code-block:: python

        mvp_parameters = setup_mvp(angle_x=0.5, angle_y=1.0, zoom=1.2, aspect=16/9)
"""

import numpy as np
from decologr import Decologr as log
from elmo.gl.shader import LegacyShaderUniformName
from pyglm import glm

from picogl.backend.gl.api.shader import (gl_get_uniform_location,
                                          gl_uniform_matrix_4fv)
from picogl.backend.legacy.core.camera.look_at import look_at
from picogl.backend.legacy.core.camera.perspective import perspective
from picogl.backend.modern.core.shader.rotation_matrix import \
    create_rotation_matrix
from picogl.boolean import GLBoolean


def setup_mvp(angle_x: float, angle_y: float, zoom: float, aspect: float) -> glm.mat4:
    """
    setup_mvp

    :param angle_x: Rotation angle around the X-axis (in radians).
    :type angle_x: float
    :param angle_y: Rotation angle around the Y-axis (in radians).
    :type angle_y: float
    :param zoom: Zoom factor controlling camera distance.
    :type zoom: float
    :param aspect: Aspect ratio of the viewport (width / height).
    :type aspect: float
    :return: Combined projection * view matrix.
    :rtype: glm.mat4

    """
    eye = glm.vec3(0, 0, 3 / zoom)
    center = glm.vec3(0, 0, 0)
    up = glm.vec3(0, 1, 0)

    # view and projection matrices
    view = glm.lookAt(eye, center, up)

    # Apply orbit rotation (same as Rx * Ry in numpy)
    view = glm.rotate(view, angle_x, glm.vec3(1, 0, 0))
    view = glm.rotate(view, angle_y, glm.vec3(0, 1, 0))

    projection = glm.perspective(glm.radians(45.0), aspect, 0.1, 100.0)

    return projection * view


def np_setup_mvp(shader: int, width: int, height: int, angle_x: float, angle_y: float, zoom: float) -> np.ndarray:
    """
    setup_mvp

    :return: ndarray[Any, dtype[bool_]]
    """
    target = np.array([0, 0, 0], dtype=np.float32)
    aspect = width / height if height > 0 else 1
    proj = perspective(45.0, aspect, 0.1, 100.0)
    # Camera orbit rotation
    rotation = create_rotation_matrix(angle_x, angle_y)
    rotated_eye = (rotation @ np.array([0, 0, 3 / zoom, 1.0], dtype=np.float32))[:3]
    rotated_up = (rotation @ np.array([0, 1, 0, 0], dtype=np.float32))[:3]
    view = look_at(rotated_eye, target, rotated_up)
    mvp = proj @ view
    mvp_loc = gl_get_uniform_location(shader, LegacyShaderUniformName.MVP_MATRIX)
    if mvp_loc == -1:
        log.error("❌ Failed to find uniform location for 'mvp_matrix'")
    else:
        gl_uniform_matrix_4fv(mvp_loc, 1, GLBoolean.TRUE, mvp.astype(np.float32))

    return mvp
