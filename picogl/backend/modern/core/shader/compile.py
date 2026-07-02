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

from OpenGL.GL import (
    glCreateShader,
    glShaderSource,
    glCompileShader,
    glGetShaderiv,
    GL_COMPILE_STATUS,
    glGetShaderInfoLog,
    glAttachShader)

# from picogl.backend.modern.core.shader.program import GLShader
from picogl.boolean import GLBoolean
from picogl.backend.modern.core.shader.helpers import log_gl_error


def gl_attach_shader(shader_program: int, shader) -> None:
    """gl attach shader"""
    glAttachShader(shader_program, shader)


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


def gl_get_shader_iv(shader: int, status: int = GL_COMPILE_STATUS) -> int:
    """
    Retrieves integer value parameters of a shader object.

    This function is used to query information about a shader object, such as its
    compile status, by retrieving a parameter specified by the `status` argument.

    Args:
        shader: Represents the identifier of the shader object whose parameter is
            being queried.
        status: Specifies the parameter to query for the shader object. Defaults
            to `GL_COMPILE_STATUS`.

    Returns:
        An integer value representing the requested parameter of the shader object.
    """
    return glGetShaderiv(shader, status)


def gl_get_shader_info_log(shader) -> str:
    """
    Retrieves the information log for a given OpenGL shader object.

    The function acts as a wrapper around OpenGL's glGetShaderInfoLog
    method, which retrieves a human-readable debugging or error log
    associated with a specified shader. This log can include
    compiler messages, warnings, or errors.

    Parameters:
    shader (int): The shader object for which the information log
    needs to be retrieved. This is usually the identifier
    returned by OpenGL when the shader was created.

    Returns:
    str: The information log associated with the given shader.
    It contains informational messages, warnings, or errors
    produced during shader compilation.

    Raises:
    TypeError: If the provided shader is not an integer.
    """
    return glGetShaderInfoLog(shader)


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
