from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_2_0 import glAttachShader


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
