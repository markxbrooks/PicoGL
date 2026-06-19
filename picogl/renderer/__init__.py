"""Renderer package exports.

Exports are loaded lazily so lightweight modules such as
``picogl.renderer.readback`` do not import the full renderer stack.
"""

__all__ = [
    "Bindable",
    "GLMesh",
    "GLResourceRegistry",
    "Initializable",
    "MeshData",
    "RendererBase",
]


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
    if name == "Initializable":
        from .initializable import Initializable

        return Initializable
    if name == "Bindable":
        from .initializable import Bindable

        return Bindable
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
