"""
This module provides functionality to interact with shader programs, enabling the
setting of uniform variables in the shader.

The module integrates external dependencies to manage uniform variable locations
and their respective values in an OpenGL-like environment.
"""
from typing import Union

import numpy as np
from decologr import Decologr as log
from pyglm import glm

from picogl.backend.modern.core.uniform.location import get_uniform_location
from picogl.backend.modern.core.uniform.location_value import \
    set_uniform_location_value


def set_uniform_name_value(
    shader_program: int,
    uniform_name: str,
    uniform_value: Union[
        float, int, glm.vec2, glm.vec3, glm.vec4, glm.mat4, np.ndarray
    ],
):
    """
    set_uniform_value

    :param shader_program: int
    :param uniform_name: Name of the uniform variable
    :param uniform_value: Value to set (supports float, int, vec2, vec3, vec4, mat4, or np.ndarray)

    Set a uniform variable in a shader program
    """
    location = get_uniform_location(shader_program, uniform_name)
    if location == -1:
        log.warning(f"Uniform '{uniform_name}' not found in shader {shader_program}.")
        return
    set_uniform_location_value(location, uniform_value)
