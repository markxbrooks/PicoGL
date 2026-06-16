import numpy as np


class GeometryData:
    """CPU side vertex data."""

    __slots__ = ("vertices", "normals", "indices", "colors")

    def __init__(
        self,
        vertices: np.ndarray | list | None = None,
        normals: np.ndarray | list | None = None,
        indices: np.ndarray | list | None = None,
        colors: np.ndarray | list | None = None,
    ):
        self.vertices = vertices  # (N, 3)
        self.normals = normals  # (N, 3)
        self.indices = indices  # (N, )
        self.colors = colors  # (N, 3)
