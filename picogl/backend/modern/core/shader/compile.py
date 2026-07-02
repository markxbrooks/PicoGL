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

from OpenGL import GL as gl

from boolean import GLBoolean
from picogl.backend.modern.core.shader.helpers import log_gl_error


def compile_shader(shader_program: int, shader_type: int, source: str):
    """
    compile_vertex_shader

    :param shader_program: int shader program
    :param shader_type: int shader type e.g. GL_VERTEX_SHADER GL_FRAGMENT_SHADER
    :param source: shader source string
    """
    shader = gl.glCreateShader(shader_type)  # pylint: disable=E1111
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    if GLBoolean.TRUE != gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        err = gl.glGetShaderInfoLog(shader)
        raise Exception(err)
    gl.glAttachShader(shader_program, shader)
    log_gl_error()
    return shader
