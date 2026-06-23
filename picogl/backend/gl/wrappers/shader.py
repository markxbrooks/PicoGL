from __future__ import annotations

from typing import Any

from OpenGL.GL import glUniformMatrix4fv, glGetUniformLocation
from OpenGL.raw.GL.VERSION.GL_2_0 import glUseProgram

from picogl.boolean import GLBoolean


def gl_use_program(shader_program: int):
    glUseProgram(shader_program)


def gl_uniform_matrix_4f(value: Any, location: int, uniform_name: str):
    glUniformMatrix4fv(
        glGetUniformLocation(location, uniform_name), 1, GLBoolean.FALSE, value
    )