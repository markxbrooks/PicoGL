"""
Provides utility functions for managing shader programs and uniform variables in OpenGL.

This module includes methods to activate shader programs, update 4x4 matrix uniform
variables, and handle uniform updates by their variable names. It serves as a utility
layer for efficient OpenGL rendering tasks.
"""

from OpenGL.GL import glCreateProgram, glGetProgramiv


def gl_create_program() -> int:
    """
    Creates a new OpenGL program object.

    This function is a wrapper for the OpenGL function `glCreateProgram`.
    It is used to create an empty program object that can later be linked
    with shader objects. A program object manages all the shaders and
    their interactions within a single OpenGL program.

    Returns:
        int: The handle to the created OpenGL program object.
    """
    return glCreateProgram()


def gl_get_program_iv(program: int, pname: int):
    """
    Retrieves a specific parameter value for a given OpenGL program object.

    This function acts as a wrapper for the OpenGL `glGetProgramiv` function, allowing
    you to query various parameters of a program object, such as its link status or
    active attribute count.

    Args:
        program (int): The OpenGL program object ID for which parameter information is requested.
        pname: The name of the program parameter to query. This should be a constant
            value defined by OpenGL, such as GL_LINK_STATUS or GL_ACTIVE_UNIFORMS.

    Returns:
        int: The queried parameter value corresponding to the given pname.
    """
    return glGetProgramiv(program, pname)