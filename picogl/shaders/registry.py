"""
ShaderRegistry
==============

Example Usage:
==============
>>> shader_registry = ShaderRegistry()
... # Load shaders at app start
... for shader_type_value in ShaderType:
...    shader_registry.load_and_add(shader_type_value)
...
... # Later...
... program = shader_registry.get(ShaderType.ATOMS)
... if program:
...     program.bind()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from decologr import Decologr as log
from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.globals import PICOGL_SHADER_SRC_DIRECTORY
from picogl.shaders.compile import compile_shaders
from picogl.shaders.load import load_fragment_and_vertex_for_shader_type
from picogl.shaders.type import ShaderType


@dataclass
class ShaderRegistry:
    """Compile and cache ``ShaderProgram`` instances by ``ShaderType``."""

    shaders: Dict[ShaderType, ShaderProgram] = field(default_factory=dict)
    shader_directory: str | Path = field(
        default_factory=lambda: PICOGL_SHADER_SRC_DIRECTORY
    )

    def load_and_add(self, shader_type: ShaderType) -> Optional[ShaderProgram]:
        """Load, compile, and register a shader program for *shader_type*."""
        try:
            vertex_src, fragment_src = load_fragment_and_vertex_for_shader_type(
                shader_type.value, str(self.shader_directory)
            )
            if not isinstance(vertex_src, str) or not isinstance(fragment_src, str):
                raise TypeError(
                    f"Expected GLSL source strings for {shader_type}, "
                    f"got {type(vertex_src)} / {type(fragment_src)}"
                )
            program = compile_shaders(
                vertex_src, fragment_src, shader_name=shader_type.value
            )
            if program:
                self.shaders[shader_type] = program
            return program
        except Exception as ex:
            log.error(
                f"❌ Failed to load shader_manager.current_shader_program "
                f"{shader_type}: {ex}"
            )
            import traceback

            traceback.print_exc()
            return None

    def get(self, shader_type: ShaderType) -> Optional[ShaderProgram]:
        return self.shaders.get(shader_type)

    def has(self, shader_type: ShaderType) -> bool:
        return shader_type in self.shaders

    def release_all(self) -> None:
        for shader_type, shader in self.shaders.items():
            if hasattr(shader, "release") and callable(shader.release):
                try:
                    shader.release()
                except Exception as e:
                    log.warning(
                        f"⚠️ Failed to release shader_manager.current_shader_program "
                        f"'{shader_type}': {e}"
                    )
        self.shaders.clear()
