"""
Provides utility functions for managing shader programs and uniform variables in OpenGL.

This module includes methods to activate shader programs, update 4x4 matrix uniform
variables, and handle uniform updates by their variable names. It serves as a utility
layer for efficient OpenGL rendering tasks.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any

import numpy as np
from OpenGL.GL import glGetUniformLocation, glUniformMatrix4fv
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_FRAGMENT_SHADER, GL_VERTEX_SHADER

from backend.gl.api.shader import gl_get_uniform_location
from boolean import GLBoolean

from picogl.boolean import GLBoolean


def gl_uniform_matrix_4fv(
    location: int, count: int, transpose: GLBoolean, value: Any
) -> None:
    """
    Sets a 4x4 matrix for a given uniform variable in the currently active shader program.

    Parameters:
    location (int): The location of the uniform variable to be updated.
    count (int): The number of matrices to be loaded. Typically 1.
    transpose (GLBoolean): Specifies whether to transpose the matrix values.
    value (Any): The matrix data to be assigned to the uniform variable.

    Returns:
    None
    """
    glUniformMatrix4fv(location, count, transpose, value)


def gl_uniform_name_matrix_4f(value: Any, location: int, uniform_name: str) -> None:
    """
    Updates a 4x4 matrix uniform variable in the OpenGL shader program.

    This function sets the value of a 4x4 matrix uniform variable within
    a specified OpenGL shader program. It locates the uniform variable
    by its name and location, then applies the given matrix value.

    Parameters:
    value : Any
        The 4x4 matrix to be used as the uniform value in the shader.
    location : int
        The reference to the OpenGL shader program.
    uniform_name : str
        The name of the uniform variable within the shader program.

    Returns:
    None
    """
    gl_uniform_matrix_4fv(
        glGetUniformLocation(location, uniform_name), 1, GLBoolean.FALSE, value
    )


class GLShader(IntEnum):
    """GL Shader"""

    VERTEX_SHADER = GL_VERTEX_SHADER
    FRAGMENT_SHADER = GL_FRAGMENT_SHADER


def gl_set_uniform_matrix(shader_program: int, shader_uniform_name: str, matrix: np.ndarray):
    """gl set uniform matrix"""
    gl_uniform_matrix_4fv(
        gl_get_uniform_location(shader_program, shader_uniform_name), 1, GLBoolean.FALSE, matrix
    )