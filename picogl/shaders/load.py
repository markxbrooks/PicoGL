"""
Shader utilities
"""

import os
from pathlib import Path
from typing import Optional


def load_shader_source_string(file_name: str | Path, directory: Optional[str] = None) -> str:
    """
    Loads a shader_manager.current_shader_program source file as a string.

    :param file_name: Shader file name (e.g., "atoms_vertex.glsl").
    :param directory: Optional base shader_directory; defaults to script's shader_directory.
    :return: Shader source code.
    :raises RuntimeError: If file not found or unreadable.
    """
    if directory is None:
        directory = os.path.dirname(os.path.abspath(__file__))
    file_name = str(file_name)
    path = os.path.join(directory, file_name)
    # print(f"📄 Loading shader_manager.current_shader_program from: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f"❌ Shader file not found: {path}")
    except Exception as ex:
        raise RuntimeError(
            f"❌ Error reading shader_manager.current_shader_program '{path}': {ex}"
        )


SHADER_SRC_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
DEFAULT_VERTEX_SHADER_SRC = load_shader_source_string(
    os.path.join(SHADER_SRC_DIRECTORY, "default_vertex.glsl")
)
DEFAULT_FRAGMENT_SHADER_SRC = load_shader_source_string(
    os.path.join(SHADER_SRC_DIRECTORY, "default_fragment.glsl")
)

class ShaderSourceType:
    """Shader Source Types"""
    vertex = "vertex"
    fragment = "fragment"


def load_fragment_and_vertex_for_shader_type(
    shader_type_value: str, shader_directory: str
) -> tuple[str, str]:
    """
    load_fragment_and_vertex_for_shader_type

    :param shader_directory: str
    :param shader_type_value: ShaderType
    :return: None
    """
    vert_path = get_shader_path(shader_type_value, ShaderSourceType.vertex)
    frag_path = get_shader_path(shader_type_value, ShaderSourceType.fragment)
    vertex_src = load_shader_source_string(vert_path, shader_directory)
    fragment_src = load_shader_source_string(frag_path, shader_directory)
    return vertex_src, fragment_src


def get_shader_path(shader_type_value: str, shader_source_type = ShaderSourceType.vertex) -> Path:
    """get shader path"""
    vert_path = Path("src") / shader_type_value / f"{shader_source_type}.glsl"
    return vert_path
