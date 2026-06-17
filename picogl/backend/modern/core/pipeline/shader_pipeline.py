"""Modern shader-based rendering pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from OpenGL.GL import glUseProgram

if TYPE_CHECKING:
    from picogl.backend.modern.core.shader.program import ShaderProgram


class ShaderPipeline:
    """Shader program binding and uniform upload for modern GL draws."""

    def __init__(self, program: "ShaderProgram | None" = None):
        self._program = program

    @property
    def program(self) -> "ShaderProgram | None":
        return self._program

    def set_program(self, program: "ShaderProgram") -> None:
        self._program = program

    def bind(self) -> None:
        if self._program is None:
            raise RuntimeError("ShaderPipeline.bind() requires a program")
        self._program.bind()

    def unbind(self) -> None:
        glUseProgram(0)

    def set_uniforms(self, uniforms: dict[str, Any]) -> None:
        if self._program is None:
            raise RuntimeError("ShaderPipeline.set_uniforms() requires a program")
        for name, value in uniforms.items():
            self._program.uniform(name, value)
