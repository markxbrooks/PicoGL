"""Sticky client-array binding for legacy immediate-mode meshes."""

from __future__ import annotations

from typing import Any

from OpenGL.GL import (
    glColorPointer,
    glDisableClientState,
    glEnableClientState,
    glNormalPointer,
    glTexCoordPointer,
    glVertexPointer,
)

from picogl.numerical import GLNumeric
from picogl.renderer.initializable import Bindable
from picogl.state.client import GLClientState


class LegacyClientMeshBinding(Bindable):
    """Sticky client-array setup for one CPU mesh; unbind disables states."""

    def __init__(self, mesh: Any) -> None:
        super().__init__()
        self._mesh = mesh

    def _do_binding(self) -> None:
        mesh = self._mesh
        if mesh.vertices is not None:
            glEnableClientState(GLClientState.VERTEX)
            glVertexPointer(3, GLNumeric.FLOAT, 0, mesh.vertices)

        if mesh.normals is not None:
            glEnableClientState(GLClientState.NORMAL)
            glNormalPointer(GLNumeric.FLOAT, 0, mesh.normals)

        if mesh.colors is not None:
            glEnableClientState(GLClientState.COLOR)
            glColorPointer(4, GLNumeric.FLOAT, 0, mesh.colors)

        if getattr(mesh, "texcoords", None) is not None:
            glEnableClientState(GLClientState.TEXCOORD)
            glTexCoordPointer(2, GLNumeric.FLOAT, 0, mesh.texcoords)

    def _do_unbinding(self) -> None:
        mesh = self._mesh
        if getattr(mesh, "texcoords", None) is not None:
            glDisableClientState(GLClientState.TEXCOORD)
        if mesh.colors is not None:
            glDisableClientState(GLClientState.COLOR)
        if mesh.normals is not None:
            glDisableClientState(GLClientState.NORMAL)
        if mesh.vertices is not None:
            glDisableClientState(GLClientState.VERTEX)
