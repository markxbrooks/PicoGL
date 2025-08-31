"""
GLContext class
"""

import numpy as np
from OpenGL import GL


class MeshData:
    """Holds OpenGL-related state objects for rendering."""

    def __init__(
        self,
        vbo: np.ndarray = None,
        nbo: np.ndarray = None,
        uvs: np.ndarray = None,
        cbo: np.ndarray = None,
        ebo: np.ndarray = None,
    ):
        """set up the OpenGL context"""
        self.vbo = vbo
        self.nbo = nbo
        self.uvs = uvs
        self.cbo = cbo
        self.ebo = ebo

        self.vertex_count = len(vbo.flatten()) // 3 if vbo is not None else None

    def as_ribbon_args(self) -> dict:
        """Convert into arguments for setup_ribbon_buffers."""
        return {
            "positions": self.vbo,
            "colors": self.cbo,
            "normals": self.nbo,
            "indices": self.ebo,
        }

    def __str__(self):
        return f"{self.vbo} {self.uvs} {self.cbo} "

    @classmethod
    def _to_float32_flat(cls, arr, name: str, required: bool = False) -> np.ndarray:
        if arr is None:
            if required:
                raise ValueError(f"{name} is required")
            return None
        a = np.asarray(arr, dtype=np.float32)
        if a.ndim > 1:
            a = a.reshape(-1)
        return a

    @classmethod
    def _to_float32_flat_or_none(cls, arr, name: str) -> np.ndarray:
        return cls._to_float32_flat(arr, name, required=False)

    @classmethod
    def _to_int32_flat(cls, arr, name: str, required: bool = False) -> np.ndarray:
        if arr is None:
            if required:
                raise ValueError(f"{name} is required")
            return None
        a = np.asarray(arr, dtype=np.int32)
        if a.ndim > 1:
            a = a.reshape(-1)
        return a

    @classmethod
    def _default_colors_for_vertices(cls, vertex_count: int) -> np.ndarray:
        # Simple default: red color per vertex
        colors = np.tile(np.array([1.0, 0.0, 0.0], dtype=np.float32), (vertex_count, 1))
        return colors.reshape(-1)

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        if self.vbo is not None:
            GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
            GL.glVertexPointer(3, GL.GL_FLOAT, 0, self.vbo)
        if self.nbo is not None:
            GL.glEnableClientState(GL.GL_NORMAL_ARRAY)
            GL.glNormalPointer(GL.GL_FLOAT, 0, self.nbo)
        if self.cbo is not None:
            GL.glEnableClientState(GL.GL_COLOR_ARRAY)
            GL.glColorPointer(3, GL.GL_FLOAT, 0, self.cbo)
        if self.uvs is not None:
            GL.glEnableClientState(GL.GL_TEXTURE_COORD_ARRAY)
            GL.glTexCoordPointer(2, GL.GL_FLOAT, 0, self.uvs)

    def unbind(self):
        if self.uvs is not None:
            GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        if self.cbo is not None:
            GL.glDisableClientState(GL.GL_COLOR_ARRAY)
        if self.nbo is not None:
            GL.glDisableClientState(GL.GL_NORMAL_ARRAY)
        if self.vbo is not None:
            GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

    @classmethod
    def from_raw(
        cls,
        vertices,
        normals=None,
        uvs=None,
        colors=None,
        indices=None,
        color_per_vertex=None,  # optional override for generated colors
    ):
        """
        Build a MeshData from raw/python inputs.

        - vertices: required, list/array of x,y,z triplets
        - normals: optional, list/array of x,y,z triplets
        - uvs: optional, list/array of u,v pairs
        - indices: optional int indices
        - colors: optional per-vertex colors (flat float32 array)
        - color_per_vertex: if provided and colors is None, generate per-vertex colors
        """
        vbo = cls._to_float32_flat(vertices, "vertices", required=True)
        vertex_count = len(vbo) // 3 if vbo is not None else 0

        nbo = cls._to_float32_flat_or_none(normals, "normals")
        if nbo is not None and len(nbo) // 3 != vertex_count:
            raise ValueError("normals length must be 3 * vertex_count")

        uvs_arr = cls._to_float32_flat_or_none(uvs, "uvs")
        if uvs_arr is not None and len(uvs_arr) // 2 != vertex_count:
            raise ValueError("uvs length must be 2 * vertex_count (if provided)")

        cbo_arr = cls._to_float32_flat_or_none(colors, "colors")

        if cbo_arr is None:
            if color_per_vertex is not None:
                # user supplied a color-per-vertex function or preset
                # If color_per_vertex is a scalar (same color for all), broadcast accordingly
                if isinstance(color_per_vertex, (list, tuple, np.ndarray)):
                    colors = np.asarray(color_per_vertex, dtype=np.float32).reshape(-1)
                    if len(colors) == 3:
                        # single color; replicate per vertex
                        cbo_arr = np.tile(colors, vertex_count)
                    elif len(colors) == vertex_count * 3:
                        cbo_arr = colors
                    else:
                        raise ValueError("color_per_vertex array length invalid")
                else:
                    raise ValueError("color_per_vertex must be array-like or None")
            else:
                # default per-vertex color (red)
                cbo_arr = cls._default_colors_for_vertices(vertex_count)
        # If cbo_arr still None and we had color_per_vertex, ensure it's flat
        if cbo_arr is not None and cbo_arr.ndim != 1:
            cbo_arr = cbo_arr.reshape(-1)

        # Indices (optional)
        indices_arr = cls._to_int32_flat(indices, "indices", required=False)

        return cls(
            vbo=vbo,
            nbo=nbo,
            uvs=uvs_arr,
            cbo=cbo_arr,
            ebo=indices_arr
        )

    def draw(self, color: tuple, line_width: float = 1.0, mode: int = GL.GL_TRIANGLES, fill: bool = False):
        """draw"""
        if fill:
            fill_mode = GL.GL_FILL
        else:
            fill_mode = GL.GL_LINE
        # Set material properties for the isosurface
        GL.glLineWidth(line_width)
        GL.glColor4f(0.0, 0.0, 1.0, 0.8)

        # Draw as wireframe for better visibility
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, fill_mode)
        GL.glColor3f(*color)
        # Draw the mesh
        GL.glDrawElements(
            mode, len(self.ebo) * 3, GL.GL_UNSIGNED_INT, self.ebo
        )
        # Restore fill mode
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
