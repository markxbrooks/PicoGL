from __future__ import annotations

from typing import Any

from OpenGL.GL import glUniformMatrix4fv, glGetUniformLocation
from OpenGL.raw.GL.VERSION.GL_2_0 import glUseProgram

from picogl.boolean import GLBoolean


def gl_uniform_matrix_4v(location: int, name, value: Any):
    """gl uniform matrix 4v"""
    glUniformMatrix4fv(
        glGetUniformLocation(location, name), 1, GLBoolean.FALSE, value
    )


def gl_use_program(shader_program: int):
    """gl use program"""
    glUseProgram(shader_program)
