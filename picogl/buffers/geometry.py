import numpy as np


class GeometryData:
    """CPU side vertex data."""
    __slots__ = ("vertices", "normals", "indices", "colors")
    def __init__(self, vertices: np.ndarray | list, normals: np.ndarray | list, indices: np.ndarray | list, colors: np.ndarray| list):
        self.vertices = vertices # (N, 3)
        self.normals = normals   # (N, 3)
        self.indices = indices   # (N, )
        self.colors = colors     # (N, 3)
