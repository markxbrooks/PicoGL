""" """

from typing import Optional, Union

from picogl.buffers.geometry import GeometryData
from picogl.buffers.vertex.meta_data import VertexMetadata
from picogl.renderer import MeshData


class VertexData:
    """
    CPU-side vertex container for rendering pipelines.

    Separates:
    - Geometry (GPU-bound)
    - Metadata (CPU-only)
    """

    __slots__ = ("geom_data", "meta_data")

    def __init__(
        self,
        geom_data: Union["GeometryData", "MeshData"],
        meta_data: Optional["VertexMetadata"] = None,
    ):
        if geom_data is None:
            raise ValueError("geom_data must not be None")

        self.geom_data = geom_data
        self.meta_data = meta_data

    def validate(self) -> None:
        """Validate internal consistency."""
        geom = self.geom_data

        n = len(geom.vertices)

        if geom.normals is not None and len(geom.normals) != n:
            raise ValueError("Normals must match vertex count")

        if geom.colors is not None and len(geom.colors) != n:
            raise ValueError("Colors must match vertex count")

        if self.meta_data is not None:
            meta = self.meta_data

            if meta.chain_ids is not None and len(meta.chain_ids) != n:
                raise ValueError("chain_ids must match vertex count")

    @property
    def vertex_count(self) -> int:
        return len(self.geom_data.vertices)

    @property
    def index_count(self) -> int:
        return len(self.geom_data.indices)
