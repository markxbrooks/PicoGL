from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_2_0 import glLinkProgram


def gl_link_program(program: int):
    """
    Links a given OpenGL program object.

    This function wraps the OpenGL glLinkProgram function, which links a
    program object specified by the "program" parameter. The program object must
    contain all the necessary shaders attached before linking.

    Args:
        program (int): The ID of the OpenGL program object to link.
    """
    glLinkProgram(program)
