"""Renderer package exports.

Exports are loaded lazily so lightweight modules such as
``picogl.renderer.readback`` do not import the full renderer stack.
"""

__all__ = [
    "Bindable",
    "GLMesh",
    "GLResourceRegistry",
    "Initializable",
    "MeshArrays",
    "MeshBuilder",
    "MeshData",
    "MeshPart",
    "PNCPart",
    "RendererBase",
    "mesh_part_from_pnc",
    "solid_color_mesh_part",
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
    if name == "MeshArrays":
        from .mesh_arrays import MeshArrays

        return MeshArrays
    if name == "MeshBuilder":
        from .mesh_builder import MeshBuilder

        return MeshBuilder
    if name == "MeshPart":
        from .mesh_builder import MeshPart

        return MeshPart
    if name == "mesh_part_from_pnc":
        from .mesh_builder import mesh_part_from_pnc

        return mesh_part_from_pnc
    if name == "solid_color_mesh_part":
        from .mesh_builder import solid_color_mesh_part

        return solid_color_mesh_part
    if name == "MeshData":
        from .meshdata import MeshData

        return MeshData
    if name == "PNCPart":
        from .meshdata import PNCPart

        return PNCPart
    if name == "Initializable":
        from .initializable import Initializable

        return Initializable
    if name == "Bindable":
        from .initializable import Bindable

        return Bindable
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
