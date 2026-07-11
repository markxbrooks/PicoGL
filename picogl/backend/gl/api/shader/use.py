from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_2_0 import glUseProgram


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
