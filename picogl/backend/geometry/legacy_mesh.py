"""Legacy client-state GPU mesh."""

from __future__ import annotations

from typing import Any

from OpenGL.GL import glDrawElements

from picogl.backend.geometry.legacy_mesh_binding import LegacyClientMeshBinding
from picogl.backend.geometry.mesh import GPUMesh
from picogl.numerical import GLNumeric


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
            glDrawElements(
                mode,
                len(self.mesh.indices),
                GLNumeric.UNSIGNED_INT,
                self.mesh.indices,
            )
