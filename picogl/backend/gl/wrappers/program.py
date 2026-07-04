"""
Provides utility functions for managing shader programs and uniform variables in OpenGL.

This module includes methods to activate shader programs, update 4x4 matrix uniform
variables, and handle uniform updates by their variable names. It serves as a utility
layer for efficient OpenGL rendering tasks.
"""

from OpenGL.GL import glCreateProgram


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