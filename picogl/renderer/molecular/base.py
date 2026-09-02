"""Base class for molecular mesh data and GPU backend adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.meshdata import MeshData

if TYPE_CHECKING:
    from picogl.renderer.glmesh import GLMesh
    from picogl.renderer.legacy_glmesh import LegacyGLMesh


class MolecularMesh(ABC):
    """
    Domain mesh that builds :class:`~picogl.renderer.meshdata.MeshData` and can
    materialize legacy or modern GPU wrappers.
    """

    draw_mode: GLDrawMode = GLDrawMode.TRIANGLES

    def __init__(self) -> None:
        self._mesh_data: Optional[MeshData] = None
        self._legacy_glmesh: Optional[LegacyGLMesh] = None

    @abstractmethod
    def build_mesh_data(self) -> MeshData:
        """Construct mesh arrays for this molecular primitive."""

    def to_mesh_data(self) -> MeshData:
        """Return cached :class:`MeshData`, building on first access."""
        if self._mesh_data is None:
            self._mesh_data = self.build_mesh_data()
        return self._mesh_data

    def to_legacy_glmesh(self, *, upload: bool = True) -> LegacyGLMesh:
        """
        Build or return a cached :class:`~picogl.renderer.legacy_glmesh.LegacyGLMesh`.

        Parameters
        ----------
        upload :
            When ``True``, upload GPU buffers immediately.
        """
        if self._legacy_glmesh is None:
            from picogl.renderer.legacy_glmesh import LegacyGLMesh

            self._legacy_glmesh = LegacyGLMesh.from_mesh_data(self.to_mesh_data())
        if upload:
            self._legacy_glmesh.upload()
        return self._legacy_glmesh

    def to_glmesh(self, *, upload: bool = True, **kwargs: Any) -> GLMesh:
        """
        Build a :class:`~picogl.renderer.glmesh.GLMesh` from this mesh data.

        Extra keyword arguments are forwarded to
        :meth:`~picogl.renderer.glmesh.GLMesh.from_mesh_data`.
        """
        from picogl.renderer.glmesh import GLMesh

        mesh = GLMesh.from_mesh_data(self.to_mesh_data(), **kwargs)
        if upload:
            mesh.upload()
        return mesh

    def draw_legacy(self, mode: Optional[GLDrawMode] = None) -> None:
        """Draw via a cached legacy GL mesh using this mesh's default mode."""
        self.to_legacy_glmesh(upload=True).draw(mode or self.draw_mode)
