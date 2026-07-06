"""
Sticky client-array binding for legacy immediate-mode meshes.
"""

from __future__ import annotations

from typing import Any

from picogl.backend.gl.state.client import GLClientState
from picogl.backend.gl.wrappers import (
    gl_disable_legacy_client_state,
    gl_enable_legacy_client_state,
)
from picogl.backend.gl.wrappers.pointer import (
    gl_color_array_pointer,
    gl_normal_array_pointer,
    gl_texcoord_array_pointer,
    gl_vertex_array_pointer,
)
from picogl.renderer.initializable import Bindable
from picogl.renderer.meshdata import MeshData


class LegacyClientMeshBinding(Bindable):
    """Sticky client-array setup for one CPU mesh; unbind disables states."""

    def __init__(self, mesh: Any) -> None:
        super().__init__()
        self._mesh: MeshData = mesh

    def _do_binding(self) -> None:
        m = self._mesh
        if m.vertices is not None:
            gl_enable_legacy_client_state(GLClientState.VERTEX)
            gl_vertex_array_pointer(pointer=m.vertices)

        if m.normals is not None:
            gl_enable_legacy_client_state(GLClientState.NORMAL)
            gl_normal_array_pointer(pointer=m.normals)

        if m.colors is not None:
            gl_enable_legacy_client_state(GLClientState.COLOR)
            gl_color_array_pointer(pointer=m.colors)

        if getattr(m, "texcoords", None) is not None:
            gl_enable_legacy_client_state(GLClientState.TEXCOORD)
            gl_texcoord_array_pointer(pointer=m.texcoords)

    def _do_unbinding(self) -> None:
        """do unbinding if mesh is unbinded."""
        mesh = self._mesh
        if getattr(mesh, "texcoords", None) is not None:
            gl_disable_legacy_client_state(GLClientState.TEXCOORD)
        if mesh.colors is not None:
            gl_disable_legacy_client_state(GLClientState.COLOR)
        if mesh.normals is not None:
            gl_disable_legacy_client_state(GLClientState.NORMAL)
        if mesh.vertices is not None:
            gl_disable_legacy_client_state(GLClientState.VERTEX)
