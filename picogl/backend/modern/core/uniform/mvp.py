"""
This module provides utilities for setting the Model-View-Projection (MVP)
matrix uniforms in a given shader program. It includes functions that
abstract the process of locating and updating uniform variables for shaders
that utilize MVP matrices.

This module primarily leverages OpenGL utilities and matrix libraries such as
numpy and pyglm to interact with shaders.

Functions:
- set_mvp_uniform: Sets the MVP matrix uniform in a given shader program.
- shader_uniform_set_mvp: Assigns the MVP matrix uniform in the shader
  program using either numpy or pyglm matrix formats.
"""

from typing import Union

import numpy as np
from decologr import Decologr as log
from elmo.gl.shader import LegacyShaderUniformName, ShaderUniformName
from pyglm import glm

from picogl.backend.gl.api.shader import gl_uniform_matrix_4fv
from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.backend.modern.core.uniform.location import gl_get_uniform_location
from picogl.boolean import GLBoolean


def set_mvp_uniform(shader: ShaderProgram = None, mvp: glm.mat4 = None) -> None:
    """
    set_mvp_uniform

    :param shader:
    :param mvp:
    :return: None
    Set the model_matrix-view-projection matrix uniform in the shader program.
    """
    mvp_loc = gl_get_uniform_location(
        shader.program, LegacyShaderUniformName.MVP_MATRIX
    )
    gl_uniform_matrix_4fv(mvp_loc, 1, GLBoolean.FALSE, glm.value_ptr(mvp))


def shader_uniform_set_mvp(
    shader_program: int, mvp_matrix: Union[np.ndarray, glm.mat4]
):
    """
    shader_uniform_set_mvp

    :param mvp_matrix: np.ndarray or glm.mat4 - model_matrix-view-projection matrix
    :param shader_program
    :return: None
    """
    mvp_loc = gl_get_uniform_location(shader_program, ShaderUniformName.MVP)
    if mvp_loc == -1:
        log.warning("Uniform 'mvp' not found in shader.")
    else:
        # Convert numpy data or glm.mat4 to float pointer
        if isinstance(mvp_matrix, np.ndarray):
            gl_uniform_matrix_4fv(
                mvp_loc, 1, GLBoolean.FALSE, mvp_matrix.astype(np.float32).flatten()
            )
        else:
            gl_uniform_matrix_4fv(
                mvp_loc, 1, GLBoolean.FALSE, glm.value_ptr(mvp_matrix)
            )
