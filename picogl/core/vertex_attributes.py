from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class VertexAttributes:
    """
    Container for per-vertex geometric attributes.
    
    Typically returned by geometry generation, analysis, or processing functions.
    Provides a clean, strongly-typed interface for positions, normals, and colors.
    
    Attributes:
        positions: (N, 3) float32 array of vertex positions
        normals: (N, 3) float32 array of vertex normals
        colors: (N, 3) float32 array of RGB vertex colors (0-1 range)
    """
    positions: np.ndarray  # (N, 3) float32
    normals: np.ndarray    # (N, 3) float32
    colors: np.ndarray     # (N, 3) float32
    
    @property
    def vertex_count(self) -> int:
        """Number of vertices."""
        return self.positions.shape[0]
    
    def to_mesh_data(self, indices: Optional[np.ndarray] = None, 
                     texcoords: Optional[np.ndarray] = None) -> "MeshData":
        """Convert to MeshData for rendering."""
        from picogl.renderer import MeshData
        return MeshData(
            vertices=self.positions,
            normals=self.normals,
            colors=self.colors,
            indices=indices,
            texcoords=texcoords
        )