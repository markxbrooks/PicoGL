from __future__ import annotations

from OpenGL.GL import glShaderSource


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
