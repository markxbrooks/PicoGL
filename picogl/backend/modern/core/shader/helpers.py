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
    shader_file_name: str | Path, glsl_dir: str | Path | None = None
) -> str:
    """
    Read shader source from a file.

    :param shader_file_name: Shader filename or already-joined path
    :param glsl_dir: Optional directory to join with a bare filename.
        Ignored when ``shader_file_name`` is absolute or already under
        ``glsl_dir`` (as ``ShaderFiles`` produces).
    :return: Shader source as a string
    """
    shader_path = Path(shader_file_name)
    if shader_path.is_absolute() or glsl_dir in (None, ""):
        abs_path = shader_path
    else:
        base = Path(glsl_dir)
        if _path_already_under(shader_path, base):
            abs_path = shader_path
        else:
            abs_path = base / shader_path

    try:
        return abs_path.read_text()
    except FileNotFoundError as ex:
        raise FileNotFoundError(f"Shader file not found: {abs_path}") from ex


def _path_already_under(path: Path, base: Path) -> bool:
    try:
        return path.is_relative_to(base)
    except (ValueError, TypeError):
        return False
