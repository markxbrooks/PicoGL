"""
Provides a wrapper for setting the value of a single uniform variable for a shader program
using the OpenGL glUniform1i function.

This module defines a function to set a uniform integer value in a shader program using
the OpenGL API. It serves as a wrapper for the corresponding low-level OpenGL method,
enabling more concise usage in Python code.
"""
from OpenGL.raw.GL.VERSION.GL_2_0 import glUniform1i


def gl_uniform1i(id, v0):
    """gl uniform"""
    glUniform1i(id, v0)

