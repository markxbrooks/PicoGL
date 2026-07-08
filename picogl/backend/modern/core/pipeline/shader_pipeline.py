"""
Modern shader-based rendering pipeline.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from picogl.backend.gl.wrappers.shader import gl_use_program
from picogl.renderer.initializable import Bindable

if TYPE_CHECKING:
    from picogl.backend.modern.core.shader.program import ShaderProgram


class ShaderPipeline(Bindable):
    """Shader program binding and uniform upload for modern gl draws."""

    def __init__(self, program: "ShaderProgram | None" = None):
        super().__init__()
        self._program = program

    @property
    def program(self) -> "ShaderProgram | None":
        return self._program

    def set_program(self, program: "ShaderProgram") -> None:
        self._program = program

    def _do_binding(self) -> None:
        if self._program is None:
            raise RuntimeError("ShaderPipeline.bind() requires a program")
        self._program.bind()

    def _do_unbinding(self) -> None:
        gl_use_program(0)

    def set_uniforms(self, uniforms: dict[str, Any]) -> None:
        if self._program is None:
            raise RuntimeError("ShaderPipeline.set_uniforms() requires a program")
        self.ensure_bound()
        for name, value in uniforms.items():
            self._program.uniform(name, value)
