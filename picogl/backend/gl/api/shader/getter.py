from __future__ import annotations

from OpenGL.GL import (
    glGetProgramInfoLog,
    glGetProgramiv,
    glGetShaderInfoLog,
    glGetShaderiv,
    glGetUniformLocation,
)
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_COMPILE_STATUS, GL_LINK_STATUS


def gl_get_uniform_location(program: int, name: str):
    """
    Retrieve the location of a uniform variable in a given shader program.

    This function retrieves the location of a uniform variable specified by its name
    from a provided shader program. The location is used to set the values of uniform
    variables in a shader during rendering. The function relies on glGetUniformLocation
    from an OpenGL context.

    Parameters:
    program (int): An integer representing the OpenGL shader program from which the
        uniform location should be retrieved.
    name: The name of the uniform variable whose location needs to be determined.

    Returns:
    int: The location of the uniform variable in the shader program. If the uniform
        variable does not exist in the program, a value of -1 will be returned.

    Raises:
    TypeError: If the parameter types are not as expected or if the input arguments
        are invalid.
    """
    return glGetUniformLocation(program, name)


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
    compiler messages, warnings, or error.

    Parameters:
    shader (int): The shader object for which the information log
    needs to be retrieved. This is usually the identifier
    returned by OpenGL when the shader was created.

    Returns:
    str: The information log associated with the given shader.
    It contains informational messages, warnings, or error
    produced during shader compilation.

    Raises:
    TypeError: If the provided shader is not an integer.
    """
    return glGetShaderInfoLog(shader)


def gl_get_program_info_log(program: int) -> int:
    """
    Returns the information log for a program object.

    This function retrieves the information log for a shader program object. The
    information log can provide details about the linking process or other states
    of the program, which can aid in debugging or understanding error in the
    program.

    Parameters:
    program (int): The handle of the program object whose information log is to
        be retrieved.

    Returns:
    int: The length of the information log, in characters, associated with the
        specified program object.
    """
    return glGetProgramInfoLog(program)


def gl_get_programiv(program: int, status: int = GL_LINK_STATUS) -> int:
    """
    Retrieves the integer value of a specific program parameter.

    This function is used to retrieve the value of a specified parameter for a given shader program.
    Primarily, it is employed to determine the status or characteristics of a shader program
    after linking or during its lifecycle.

    Parameters:
    program (int): The handle of the shader program whose parameter is to be retrieved.
    status (int): The specific program parameter to query. Default is GL_LINK_STATUS.

    Returns:
    int: The integer value of the specified program parameter.
    """
    return glGetProgramiv(program, status)


def gl_get_program_iv(program: int, pname: int):
    """
    Retrieves a specific parameter value for a given OpenGL program object.

    This function acts as a wrapper for the OpenGL `glGetProgramiv` function, allowing
    you to query various parameters of a program object, such as its link status or
    active attribute count.

    Args:
        program (int): The OpenGL program object ID for which parameter information is requested.
        pname: The name of the program parameter to query. This should be a constant
            value defined by OpenGL, such as GL_LINK_STATUS or GL_ACTIVE_UNIFORMS.

    Returns:
        int: The queried parameter value corresponding to the given pname.
    """
    return glGetProgramiv(program, pname)
