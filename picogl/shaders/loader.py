"""Shader source loading and compilation (stateless; used by :class:`ShaderManager`)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from decologr import Decologr as log

from picogl.backend.modern.core.shader.context import gl_context_available
from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.globals import SHADER_SRC_DIRECTORY
from picogl.shaders.compile import compile_shaders
from picogl.shaders.generate import generate_shader_programs
from picogl.shaders.load import (load_fragment_and_vertex_for_shader_type,
                                 load_shader_source_string)
from picogl.shaders.type import ShaderType


@dataclass(frozen=True)
class ShaderLoadResult:
    """Outcome of compiling one :class:`ShaderType`."""

    shader: ShaderProgram | None
    used_fallback: bool = False


class ShaderFallback:
    """Lazy fallback GLSL program provider."""

    def __init__(self, shader_directory: str = "") -> None:
        self.shader_directory = shader_directory
        self._program: ShaderProgram | None = None

    def program(self) -> ShaderProgram | None:
        if self._program is not None:
            return self._program
        if not gl_context_available():
            return None
        try:
            vert, frag = self._sources()
            self._program = compile_shaders(vert, frag, "fallback")
            log.message(
                "Fallback shader program compiled",
                silent=True,
                scope="ShaderFallback",
            )
        except Exception as ex:
            log.error(f"Fallback shader setup failed: {ex}", scope="ShaderFallback")
        return self._program

    def release(self) -> None:
        if self._program is not None:
            try:
                self._program.release()
            except Exception:
                pass
            self._program = None

    def _sources(self) -> tuple[str, str]:
        if self.shader_directory:
            base = Path(self.shader_directory)
            root = base / "src" if (base / "src").is_dir() else base
            fallback_dir = root / "fallback"
            vert_path = fallback_dir / "vertex.glsl"
            frag_path = fallback_dir / "fragment.glsl"
            if vert_path.is_file() and frag_path.is_file():
                return (
                    load_shader_source_string(str(vert_path)),
                    load_shader_source_string(str(frag_path)),
                )
        return (
            load_shader_source_string("fallback_vertex.glsl", SHADER_SRC_DIRECTORY),
            load_shader_source_string("fallback_fragment.glsl", SHADER_SRC_DIRECTORY),
        )


class ShaderLoader:
    """Compile ``ShaderType`` GLSL pairs from a shader root directory."""

    def __init__(self, shader_directory: str) -> None:
        self.shader_directory = shader_directory
        self.fallback = ShaderFallback(shader_directory)

    def set_directory(self, shader_directory: str) -> None:
        if shader_directory != self.shader_directory:
            self.shader_directory = shader_directory
            self.fallback.shader_directory = shader_directory

    def load(self, shader_type: ShaderType) -> ShaderLoadResult:
        if not gl_context_available():
            log.warning(
                f"Cannot compile shader {shader_type}: no current OpenGL context",
                scope="ShaderLoader",
            )
            return ShaderLoadResult(shader=None)
        try:
            vertex_src, fragment_src = load_fragment_and_vertex_for_shader_type(
                shader_type.value, self.shader_directory
            )
            program = generate_shader_programs(vertex_src, fragment_src, shader_type)
            if program:
                return ShaderLoadResult(shader=program)
            log.warning(
                f"Compile returned None for {shader_type}", scope="ShaderLoader"
            )
        except Exception as ex:
            log.warning(
                f"Shader load failed for {shader_type} in {self.shader_directory}: {ex}",
                scope="ShaderLoader",
            )
        return ShaderLoadResult(shader=None)
