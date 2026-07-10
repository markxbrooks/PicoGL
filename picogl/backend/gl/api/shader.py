"""
Provides utility functions for managing shader programs and uniform variables in OpenGL.

This module includes methods to activate shader programs, update 4x4 matrix uniform
variables, and handle uniform updates by their variable names. It serves as a utility
layer for efficient OpenGL rendering tasks.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any

from OpenGL.GL import (glGetProgramInfoLog, glGetProgramiv, glGetShaderInfoLog,
                       glGetShaderiv, glGetUniformLocation, glShaderSource,
                       glUniformMatrix4fv)
from OpenGL.raw.GL.VERSION.GL_2_0 import (GL_COMPILE_STATUS,
                                          GL_FRAGMENT_SHADER, GL_LINK_STATUS,
                                          GL_VERTEX_SHADER, glAttachShader,
                                          glCompileShader, glCreateShader,
                                          glLinkProgram, glUseProgram)
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


def gl_attach_shader(shader_program: int, shader: int) -> None:
    """
    Attaches a shader object to a shader program. This function is used as part
    of the process to create a complete shader program by linking one or more
    compiled shader objects.

    Parameters:
    shader_program: int
        The handle of the shader program to which the shader will be attached.
    shader
        The handle of the shader object to attach.

    Returns:
    None
    """
    glAttachShader(shader_program, shader)


def gl_create_shader(shader_type: "GLShader") -> int:
    """
    Creates a new shader object and returns its unique ID.

    Shaders are fundamental components of the shader pipeline in
    OpenGL, used to process vertex and fragment data in rendering. This
    function wraps the OpenGL call to create a shader object of
    a specified type.

    Parameters:
    shader_type: GLShader
        The type of the shader to be created. Common types include
        GL_VERTEX_SHADER and GL_FRAGMENT_SHADER.

    Returns:
    int
        The unique identifier of the created shader.

    Raises:
    Exception
        If shader creation fails due to invalid shader type or
        OpenGL-related issues.
    """
    return glCreateShader(shader_type)


def gl_shader_source(shader: int, source: str):
    """
    Replaces the source code in a given shader object with new source code. The function
    associates a specified shader object with a string containing the shader source.

    Args:
        shader (int): An integer handle identifying the shader object.
        source (str): A string containing the GLSL source code to be loaded
            into the shader.

    Returns:
        None
    """
    glShaderSource(shader, source)


def gl_compile_shader(shader: int):
    """
    Compiles a specified OpenGL shader. This function wraps the OpenGL
    `glCompileShader` call and initiates the compilation process for the given
    shader.

    Raises
    ------
    RuntimeError
        If an OpenGL error is encountered during the shader compilation process.

    Parameters
    ----------
    shader : int
        The handle or ID of the shader to compile. This must be a valid shader
        object created using OpenGL before calling this function.
    """
    glCompileShader(shader)


def gl_get_shader_iv(shader: int, status: int = GL_COMPILE_STATUS) -> int:
    """
    Retrieves integer value parameters of a shader object.

    This function is used to query information about a shader object, such as its
    compile status, by retrieving a parameter specified by the `status` argument.

    Args:
        shader: Represents the identifier of the shader object whose parameter is
            being queried.
        status: Specifies the parameter to query for the shader object. Defaults
            to `GL_COMPILE_STATUS`.

    Returns:
        An integer value representing the requested parameter of the shader object.
    """
    return glGetShaderiv(shader, status)


def gl_get_shader_info_log(shader) -> str:
    """
    Retrieves the information log for a given OpenGL shader object.

    The function acts as a wrapper around OpenGL's glGetShaderInfoLog
    method, which retrieves a human-readable debugging or error log
    associated with a specified shader. This log can include
    compiler messages, warnings, or errors.

    Parameters:
    shader (int): The shader object for which the information log
    needs to be retrieved. This is usually the identifier
    returned by OpenGL when the shader was created.

    Returns:
    str: The information log associated with the given shader.
    It contains informational messages, warnings, or errors
    produced during shader compilation.

    Raises:
    TypeError: If the provided shader is not an integer.
    """
    return glGetShaderInfoLog(shader)


def gl_get_program_info_log(program: int) -> int:
    """
    Returns the information log for a program object.

    This function retrieves the information log for a shader program object. The
    information log can provide details about the linking process or other states
    of the program, which can aid in debugging or understanding errors in the
    program.

    Parameters:
    program (int): The handle of the program object whose information log is to
        be retrieved.

    Returns:
    int: The length of the information log, in characters, associated with the
        specified program object.
    """
    return glGetProgramInfoLog(program)


def gl_link_program(program: int):
    """
    Links a given OpenGL program object.

    This function wraps the OpenGL glLinkProgram function, which links a
    program object specified by the "program" parameter. The program object must
    contain all the necessary shaders attached before linking.

    Args:
        program (int): The ID of the OpenGL program object to link.
    """
    glLinkProgram(program)


def gl_get_programiv(program: int, status: int = GL_LINK_STATUS) -> int:
    """
    Retrieves the integer value of a specific program parameter.

    This function is used to retrieve the value of a specified parameter for a given shader program.
    Primarily, it is employed to determine the status or characteristics of a shader program
    after linking or during its lifecycle.

    Parameters:
    program (int): The handle of the shader program whose parameter is to be retrieved.
    status (int): The specific program parameter to query. Default is GL_LINK_STATUS.

    Returns:
    int: The integer value of the specified program parameter.
    """
    return glGetProgramiv(program, status)


def gl_use_program(shader_program: int) -> None:
    """
    Sets the active shader program for subsequent rendering operations.

    This function enables the use of a specific shader program for OpenGL
    rendering. Once set, all subsequent rendering operations will utilize
    the provided shader program until a different program is set or the
    shader program is disabled.

    Parameters:
    shader_program: int
        The ID of the OpenGL shader program to be activated.

    Returns:
    None
    """
    glUseProgram(shader_program)


class GLShader(IntEnum):
    """GL Shader"""

    VERTEX_SHADER = GL_VERTEX_SHADER
    FRAGMENT_SHADER = GL_FRAGMENT_SHADER
