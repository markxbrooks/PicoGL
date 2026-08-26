"""
Provides functionality for setting a uniform variable in a shader program.

This module contains a single function that allows setting various types of
uniform variables (e.g., float, int, vectors, matrices, numpy arrays, and
sequences) for use in OpenGL shader programs. The function dynamically
handles different data types and ensures correctness when passing values
to the shader.

Function:
- set_uniform_location_value: Sets the value of a specified uniform variable
  in an OpenGL shader program.
"""

from typing import Sequence, Union

import numpy as np
from decologr import Decologr as log
from OpenGL.GL import glUniformMatrix4fv
from OpenGL.raw.GL._types import GL_FALSE
from OpenGL.raw.GL.VERSION.GL_2_0 import (glUniform1f, glUniform1i,
                                          glUniform2fv, glUniform3fv,
                                          glUniform4fv)
from pyglm import glm


def set_uniform_location_value(
    location: int,
    uniform_value: Union[
        float,
        int,
        glm.vec2,
        glm.vec3,
        glm.vec4,
        glm.mat4,
        np.ndarray,
        Sequence[float],
    ],
):
    """
    set_uniform_value

    :param uniform location:  int
    :param uniform_value: Value to set (supports float, int, vec2, vec3, vec4, mat4,
        np.ndarray, or a 2/3/4-length float sequence)

    Set a uniform variable in a shader program
    """
    # Handle types
    if isinstance(uniform_value, float):
        glUniform1f(location, uniform_value)
    elif isinstance(uniform_value, int):
        glUniform1i(location, uniform_value)
    elif isinstance(uniform_value, glm.vec2):
        glUniform2fv(location, 1, glm.value_ptr(uniform_value))
    elif isinstance(uniform_value, glm.vec3):
        glUniform3fv(location, 1, glm.value_ptr(uniform_value))
    elif isinstance(uniform_value, glm.vec4):
        glUniform4fv(location, 1, glm.value_ptr(uniform_value))
    elif isinstance(uniform_value, glm.mat4):
        glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(uniform_value))
    elif isinstance(uniform_value, np.ndarray):
        if uniform_value.shape == (4, 4):  # mat4
            glUniformMatrix4fv(
                location, 1, GL_FALSE, uniform_value.astype(np.float32).flatten()
            )
        elif uniform_value.shape == (3,):  # vec3
            glUniform3fv(location, 1, uniform_value.astype(np.float32))
        elif uniform_value.shape == (4,):  # vec4
            glUniform4fv(location, 1, uniform_value.astype(np.float32))
        elif uniform_value.shape == (2,):  # vec2
            glUniform2fv(location, 1, uniform_value.astype(np.float32))
        else:
            log.warning(
                f"Unsupported ndarray shape {uniform_value.shape} for uniform '{location}'"
            )
    elif isinstance(uniform_value, (list, tuple)):
        arr = np.asarray(uniform_value, dtype=np.float32)
        if arr.shape == (3,):
            glUniform3fv(location, 1, arr)
        elif arr.shape == (4,):
            glUniform4fv(location, 1, arr)
        elif arr.shape == (2,):
            glUniform2fv(location, 1, arr)
        else:
            log.warning(
                f"Unsupported sequence length {arr.shape} for uniform '{location}'"
            )
    else:
        log.warning(f"Unsupported uniform type for '{location}': {type(uniform_value)}")
