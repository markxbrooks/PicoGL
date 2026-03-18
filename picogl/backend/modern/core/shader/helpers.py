"""
Shader Compilation
"""

from pathlib import Path

from decologr import Decologr as log
from OpenGL import GL
from OpenGL.raw.GLU import gluErrorString


def log_gl_error():
    """
    log_gl_error
    """
    err = GL.glGetError()  # pylint: disable=E1111
    if err != GL.GL_NO_ERROR:
        log.error(f"GL ERROR: {gluErrorString(err)}")  # pylint: disable=E1101


def compile_shader(program: int, shader: int, shader_source_list: str):
    """
    compile_shader

    :param program: int
    :param shader: int
    :param shader_source_list: list
    """
    GL.glShaderSource(shader, shader_source_list)
    GL.glCompileShader(shader)
    if GL.GL_TRUE != GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
        err = GL.glGetShaderInfoLog(shader)
        raise Exception(err)
    GL.glAttachShader(program, shader)


def read_shader_source(
    shader_file_name: str, glsl_dir: str | Path | None = None
) -> str:
    """
    Read shader source from a file.

    :param shader_file_name: Name of the shader file
    :param glsl_dir: Base directory (str or Path). Defaults to project root.
    :return: Shader source as a string
    """
    if glsl_dir is None or glsl_dir == "":
        glsl_dir = Path(__file__).resolve().parent.parent
    else:
        glsl_dir = Path(glsl_dir)

    abs_path = glsl_dir / shader_file_name

    try:
        return abs_path.read_text()
    except FileNotFoundError as ex:
        raise FileNotFoundError(f"Shader file not found: {abs_path}") from ex
