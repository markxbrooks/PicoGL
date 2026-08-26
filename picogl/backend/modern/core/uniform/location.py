"""
A utility function to retrieve the location of a uniform variable in a shader program.

This module provides a wrapper function for the OpenGL `glGetUniformLocation` method
to simplify the process of obtaining the location of a uniform variable within a
specific shader program. The function requires a valid shader program identifier
and the name of the uniform variable as input and returns its corresponding location.

Functions:
- gl_get_uniform_location: Fetches the location of a uniform variable.

"""

from OpenGL.GL import glGetUniformLocation


def gl_get_uniform_location(shader_program: int, uniform_name: str) -> int:
    """
    gl_get_uniform_location

    :param shader_program: int
    :param uniform_name: str
    :return: int
    """
    location = glGetUniformLocation(shader_program, uniform_name)
    return location
