"""Legacy client-state GPU mesh."""

from __future__ import annotations

from typing import Any

from picogl.backend.geometry.legacy_mesh_binding import LegacyClientMeshBinding
from picogl.backend.geometry.mesh import GPUMesh
from picogl.core.enums.numerical import GLNumeric
from picogl.wrappers.draw import gl_draw_elements


class LegacyMesh(GPUMesh):
    """Client-array mesh binding from CPU ``MeshData`` or compatible objects."""

    def __init__(self, mesh: Any):
        self.mesh = mesh
        self._binding = LegacyClientMeshBinding(mesh)

    def bind(self) -> None:
        self._binding.ensure_bound()

    def unbind(self) -> None:
        self._binding.unbind()

    def draw(self, mode: int) -> None:
        if self.mesh.indices is not None:
            gl_draw_elements(
                len(self.mesh.indices),
                GLNumeric.UNSIGNED_INT,
                mode,
                pointer=self.mesh.indices,
            )
