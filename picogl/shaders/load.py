"""
Shader utilities
"""

import os
from pathlib import Path
from typing import Optional

from picogl.globals import PICOGL_SHADER_SRC_DIRECTORY


# from picoui.resources import resource_path


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


DEFAULT_VERTEX_SHADER_SRC = load_shader_source_string(
    os.path.join(PICOGL_SHADER_SRC_DIRECTORY, "default_vertex.glsl")
)
DEFAULT_FRAGMENT_SHADER_SRC = load_shader_source_string(
    os.path.join(PICOGL_SHADER_SRC_DIRECTORY, "default_fragment.glsl")
    # resource_path(os.path.join(SHADER_SRC_DIRECTORY, "default_fragment.glsl"))
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
    base_dir = Path(shader_directory) if shader_directory else PICOGL_SHADER_SRC_DIRECTORY
    # Support both bases:
    # - <base>/src/<shader_type>/<stage>.glsl
    # - <base>/<shader_type>/<stage>.glsl
    # This keeps compatibility with external shader roots (e.g. ElMo shaders/src).
    if (base_dir / "src").is_dir():
        root = base_dir / "src"
    else:
        root = base_dir

    vert_path = root / get_shader_path(shader_type_value, ShaderSourceType.vertex)
    frag_path = root / get_shader_path(shader_type_value, ShaderSourceType.fragment)
    vertex_src = load_shader_source_string(str(vert_path))
    fragment_src = load_shader_source_string(str(frag_path))
    return vertex_src, fragment_src

def get_shader_path(shader_type_value: str, shader_source_type = ShaderSourceType.vertex) -> Path:
    """get shader path"""
    return Path(shader_type_value) / f"{shader_source_type}.glsl"
