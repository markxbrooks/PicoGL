from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_2_0 import glCompileShader


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
