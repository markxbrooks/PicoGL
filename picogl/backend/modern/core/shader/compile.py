"""
Utility function for compiling and attaching a shader to a shader program.

This function creates a shader of the specified type, sets its source,
compiles it, and attaches it to the given shader program. If the compilation
fails, an exception is raised with the compilation error message.

:param shader_program: Shader program ID to which the compiled shader will
                       be attached.
:type shader_program: int
:param shader_type: Type of shader to compile (e.g., GL_VERTEX_SHADER,
                    GL_FRAGMENT_SHADER).
:type shader_type: int
:param source: GLSL source code of the shader to compile.
:type source: str

:return: Shader ID of the compiled shader.
:rtype: int

:raises Exception: If the shader compilation fails, an exception is raised
                   with the associated error log.
"""

from OpenGL.GL import GL_COMPILE_STATUS
from picogl.backend.gl.wrappers.shader import (
    gl_attach_shader,
    gl_compile_shader,
    gl_create_shader,
    gl_get_shader_info_log,
    gl_get_shader_iv,
    gl_shader_source,
)
from picogl.backend.modern.core.shader.helpers import log_gl_error

# from picogl.backend.modern.core.shader.program import GLShader
from picogl.boolean import GLBoolean


def compile_shader(shader_program: int, shader_type: "GLShader", source: str):
    """
    compile_vertex_shader

    :param shader_program: int shader program
    :param shader_type: int shader type e.g. GL_VERTEX_SHADER GL_FRAGMENT_SHADER
    :param source: shader source string
    """
    shader = gl_create_shader(shader_type)  # pylint: disable=E1111
    gl_shader_source(shader, source)
    gl_compile_shader(shader)
    if GLBoolean.TRUE != gl_get_shader_iv(shader, GL_COMPILE_STATUS):
        err = gl_get_shader_info_log(shader)
        raise Exception(err)
    gl_attach_shader(shader_program, shader)
    log_gl_error()
    return shader
