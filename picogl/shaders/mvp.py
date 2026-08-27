import numpy as np
from OpenGL.GL import glUniformMatrix4fv
from OpenGL.raw.GL._types import GL_FALSE
from picogl.backend.glm.glm import glm_identity_matrix
from picogl.backend.modern.core.shader.helpers import log_gl_error
from picogl.core.camera import FOVY, CameraParameters, ProjectionConfig
from pyglm import glm


def calculate_mvp_matrix(context: object, width: int = 1920, height: int = 1080):
    """
    calculate_mvp_matrix

    :param context: GlContext
    :param width: int
    :param height: int
    """
    context.projection = ProjectionConfig(
        fovy=FOVY,
        aspect=float(width) / float(max(height, 1)),
        near=ProjectionConfig().near,
        far=ProjectionConfig().far,
    ).matrix()
    # Tutorial default: eye at (4, 3, -3), looking at origin.
    camera = CameraParameters(eye=glm.vec3(4, 3, -3))
    context.view = camera.view_matrix()
    context.model = glm_identity_matrix()
    context.mvp_matrix = context.projection * context.view * context.model


def set_mvp_matrix_to_uniform_id(mvp_id: int, mvp_matrix: np.ndarray) -> None:
    """
    set_mvp_matrix_to_uniform_id

    :param mvp_id: int
    :param mvp_matrix: np.ndarray
    :return: None
    """
    glUniformMatrix4fv(mvp_id, 1, GL_FALSE, glm.value_ptr(mvp_matrix))
    log_gl_error()
