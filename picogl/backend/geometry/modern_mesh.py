"""Modern VAO-based GPU mesh."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from picogl.backend.geometry.mesh import GPUMesh
from picogl.backend.gl.api import gl_draw_elements
from picogl.backend.gl.enums import GLNumeric

if TYPE_CHECKING:
    from picogl.renderer.glmesh import GLMesh


class ModernMesh(GPUMesh):
    """VAO-backed mesh; wraps :class:`GLMesh` or a pre-uploaded VAO object."""

    def __init__(
        self,
        *,
        gl_mesh: Optional["GLMesh"] = None,
        vao: Any = None,
        index_count: int = 0,
    ):
        if gl_mesh is None and vao is None:
            raise ValueError("ModernMesh requires gl_mesh or vao")
        self._gl_mesh = gl_mesh
        self._vao = vao if gl_mesh is None else gl_mesh.vao
        self._index_count = index_count if gl_mesh is None else gl_mesh.index_count

    def bind(self) -> None:
        if self._gl_mesh is not None:
            self._gl_mesh.upload()
            self._gl_mesh.bind()
            return
        if self._vao is not None and hasattr(self._vao, "__enter__"):
            self._vao.__enter__()

    def unbind(self) -> None:
        if self._gl_mesh is not None:
            self._gl_mesh.unbind()
        elif self._vao is not None and hasattr(self._vao, "__exit__"):
            self._vao.__exit__(None, None, None)

    def draw(self, mode: int) -> None:
        if self._gl_mesh is not None:
            self._gl_mesh.draw(mode=mode)
            return
        if getattr(self._vao, "ebo", None) is not None:
            gl_draw_elements(
                self._index_count,
                GLNumeric.UNSIGNED_INT,
                mode,
                pointer=None,
            )
        elif hasattr(self._vao, "draw"):
            self._vao.draw(index_count=self._index_count, mode=mode)

    def delete(self) -> None:
        if self._gl_mesh is not None:
            self._gl_mesh.delete()
