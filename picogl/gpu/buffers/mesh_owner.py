"""CPU MeshData ownership for GPU drawables."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from picogl.renderer.meshdata import MeshData


class MeshDataOwner:
    """Expose attached :class:`~picogl.renderer.meshdata.MeshData` as ``mesh_data``.

    Storage remains the ``mesh`` attribute set by
    :meth:`~picogl.renderer.meshdata.MeshData.attach_vao`.
    """

    @property
    def mesh_data(self) -> Optional[MeshData]:
        """Return the CPU mesh attached to this drawable, if any."""
        from picogl.renderer.meshdata import MeshData as MeshDataType

        mesh = getattr(self, "mesh", None)
        return mesh if isinstance(mesh, MeshDataType) else None


class MeshChildOwner:
    """Delegate ``mesh_data`` to a child GPU drawable stored on ``.vao``.

    Used by wrapper groups (atom/bond buffer groups) that hold a VAO or VBG
    rather than owning :class:`~picogl.renderer.meshdata.MeshData` themselves.
    """

    @property
    def mesh_data(self) -> Optional[MeshData]:
        """Return the CPU mesh on the child VAO/VBG, if any."""
        from picogl.renderer.meshdata import MeshData as MeshDataType

        child = getattr(self, "vao", None)
        if child is None or isinstance(child, int):
            return None
        mesh = getattr(child, "mesh_data", None)
        return mesh if isinstance(mesh, MeshDataType) else None
