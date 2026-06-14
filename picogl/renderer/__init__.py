"""Renderer package exports.

Exports are loaded lazily so lightweight modules such as
``picogl.renderer.readback`` do not import the full renderer stack.
"""

__all__ = ["GLMesh", "GLResourceRegistry", "MeshData", "RendererBase"]


def __getattr__(name):
    if name == "RendererBase":
        from .base import RendererBase

        return RendererBase
    if name == "GLMesh":
        from .glmesh import GLMesh

        return GLMesh
    if name == "GLResourceRegistry":
        from .glresourceregistry import GLResourceRegistry

        return GLResourceRegistry
    if name == "MeshData":
        from .meshdata import MeshData

        return MeshData
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
