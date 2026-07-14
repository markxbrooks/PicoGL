from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_2_0 import glCreateProgram, glCreateShader

from picogl.backend.gl.api.shader.uniform import GLShader


def gl_create_shader(shader_type: "GLShader") -> int:
    """
    Creates a new shader object and returns its unique ID.

    Shaders are fundamental components of the shader pipeline in
    OpenGL, used to process vertex and fragment data in rendering. This
    function wraps the OpenGL call to create a shader object of
    a specified type.

    Parameters:
    shader_type: GLShader
        The type of the shader to be created. Common types include
        GL_VERTEX_SHADER and GL_FRAGMENT_SHADER.

    Returns:
    int
        The unique identifier of the created shader.

    Raises:
    Exception
        If shader creation fails due to invalid shader type or
        OpenGL-related issues.
    """
    return glCreateShader(shader_type)


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
