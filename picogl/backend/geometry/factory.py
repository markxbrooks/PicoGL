"""Binding strategies that upload CPU meshes to GPU representations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from picogl.backend.geometry.legacy_mesh import LegacyMesh
from picogl.backend.geometry.mesh import GPUMesh
from picogl.backend.geometry.modern_mesh import ModernMesh
from picogl.backend.state import gl_value

if TYPE_CHECKING:
    from picogl.renderer.meshdata import MeshData


class GLBindingStrategy(ABC):
    """Upload CPU mesh data to a reusable :class:`GPUMesh`."""

    def __init__(self):
        self._last_gpu_mesh: GPUMesh | None = None

    @abstractmethod
    def upload(self, mesh: "MeshData") -> GPUMesh: ...

    def bind_mesh(self, mesh) -> None:
        """Deprecated: upload, bind, and remember mesh for the next draw."""
        self._last_gpu_mesh = self.upload(mesh)
        self._last_gpu_mesh.bind()

    def draw(self, mesh, mode) -> None:
        """Deprecated: draw the last bound mesh, or upload on demand."""
        gpu_mesh = self._last_gpu_mesh
        if gpu_mesh is None:
            gpu_mesh = self.upload(mesh)
        gpu_mesh.draw(gl_value(mode))


class LegacyBinding(GLBindingStrategy):
    """Upload ``MeshData`` to a client-state :class:`LegacyMesh`."""

    def upload(self, mesh: "MeshData") -> GPUMesh:
        return LegacyMesh(mesh)


class ModernBinding(GLBindingStrategy):
    """Upload ``MeshData`` to a VAO-backed :class:`ModernMesh`."""

    def upload(self, mesh: "MeshData") -> GPUMesh:
        from picogl.renderer.glmesh import GLMesh

        gl_mesh = GLMesh.from_mesh_data(mesh)
        gl_mesh.upload()
        return ModernMesh(gl_mesh=gl_mesh)

    def upload_gpu_object(self, mesh: Any) -> GPUMesh:
        """Wrap an object that already has ``vao`` / ``ebo`` / ``index_count``."""
        if hasattr(mesh, "vao") and mesh.vao is not None:
            return ModernMesh(vao=mesh.vao, index_count=int(mesh.index_count))
        if hasattr(mesh, "ebo") and mesh.ebo is not None:
            return ModernMesh(vao=mesh, index_count=int(mesh.index_count))
        return self.upload(mesh)

    def bind_mesh(self, mesh) -> None:
        self._last_gpu_mesh = self.upload_gpu_object(mesh)
        self._last_gpu_mesh.bind()
