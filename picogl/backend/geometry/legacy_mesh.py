"""Legacy client-state GPU mesh."""

from __future__ import annotations

from typing import Any

from OpenGL.GL import (
    glColorPointer,
    glDrawElements,
    glEnableClientState,
    glNormalPointer,
    glTexCoordPointer,
    glVertexPointer,
)

from picogl.backend.geometry.mesh import GPUMesh
from picogl.numerical import GLNumeric
from picogl.state.client import GLClientState


class LegacyMesh(GPUMesh):
    """Client-array mesh binding from CPU ``MeshData`` or compatible objects."""

    def __init__(self, mesh: Any):
        self.mesh = mesh

    def bind(self) -> None:
        mesh = self.mesh
        if mesh.vertices is not None:
            glEnableClientState(GLClientState.VERTEX)
            glVertexPointer(3, GLNumeric.FLOAT, 0, mesh.vertices)

        if mesh.normals is not None:
            glEnableClientState(GLClientState.NORMAL)
            glNormalPointer(GLNumeric.FLOAT, 0, mesh.normals)

        if mesh.colors is not None:
            glEnableClientState(GLClientState.COLOR)
            glColorPointer(4, GLNumeric.FLOAT, 0, mesh.colors)

        if mesh.texcoords is not None:
            glEnableClientState(GLClientState.TEXCOORD)
            glTexCoordPointer(2, GLNumeric.FLOAT, 0, mesh.texcoords)

    def draw(self, mode: int) -> None:
        if self.mesh.indices is not None:
            glDrawElements(
                mode,
                len(self.mesh.indices),
                GLNumeric.UNSIGNED_INT,
                self.mesh.indices,
            )
