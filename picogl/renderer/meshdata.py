"""
GLContext class
"""

import numpy as np
from OpenGL import GL


def compute_vertex_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """
    vertices: (N, 3)
    faces:    (M, 3)  0-based indices
    returns:  (N, 3) normalized vertex normals
    """
    normals = np.zeros_like(vertices, dtype=np.float32)
    # gather vertices per triangle
    v0 = vertices[faces[:, 0]]
    v1 = vertices[faces[:, 1]]
    v2 = vertices[faces[:, 2]]

    face_normals = np.cross(v1 - v0, v2 - v0)
    # accumulate
    for i in range(3):
        np.add.at(normals, faces[:, i], face_normals)

    # normalize
    lengths = np.linalg.norm(normals, axis=1)
    normals[lengths > 0] /= lengths[lengths > 0][:, None]
    return normals


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
        # Simple default: red colour per vertex
        colors = np.tile(np.array([1.0, 0.0, 0.0], dtype=np.float32), (vertex_count, 1))
        return colors.reshape(-1)

    @classmethod
    def _default_normals_for_vertices(cls, vertex_count: int) -> np.ndarray:
        # Simple default: red colour per vertex
        normals = np.tile([0.0, 0.0, 1.0], (vertex_count, 1)).astype(np.float32)
        return normals.reshape(-1)

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        if self.vbo is not None:
            GL.gl_enableClientState(GL.GL_VERTEX_ARRAY)
            GL.glVertexPointer(3, GL.GL_FLOAT, 0, self.vbo)
        if self.nbo is not None:
            GL.gl_enableClientState(GL.GL_NORMAL_ARRAY)
            GL.glNormalPointer(GL.GL_FLOAT, 0, self.nbo)
        if self.cbo is not None:
            GL.gl_enableClientState(GL.GL_COLOR_ARRAY)
            GL.glColorPointer(3, GL.GL_FLOAT, 0, self.cbo)
        if self.uvs is not None:
            GL.gl_enableClientState(GL.GL_TEXTURE_COORD_ARRAY)
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
        vertices: np.ndarray,
        normals: np.ndarray = None,
        uvs: np.ndarray = None,
        colors: np.ndarray = None,
        indices: np.ndarray = None,
        color_per_vertex: np.ndarray = None,  # optional override for generated colors
    ):
        """
        Build a MeshData from raw/python inputs.

        :param vertices: np.ndarray required, list/array of x,y,z triplets
        :param normals: np.ndarray optional, list/array of x,y,z triplets
        :param uvs: np.ndarray optional, list/array of u,v pairs
        :param indices: np.ndarray optional int indices
        :param colors: np.ndarray optional per-vertex colors (flat float32 array)
        :param color_per_vertex: np.ndarray if provided and colors is None, generate per-vertex colors
        """
        vbo = cls._to_float32_flat(vertices, "vertices", required=True)
        vertex_count = len(vbo) // 3 if vbo is not None else 0

        num_vertices = len(vertices)
        if normals is None:
            """if indices is not None:
                indices = np.asarray(indices, dtype=np.uint32).reshape(-1)
                normals = compute_vertex_normals(vertices=vertices, faces=indices)
            else:"""
            normals = np.zeros((num_vertices, 3), dtype=np.float32)

        nbo = cls._to_float32_flat_or_none(normals, "normals")

        if nbo is not None:
            expected = num_vertices * 3
            """if len(nbo) != expected:
                raise ValueError(
                    f"normals length {len(nbo)} does not match 3 * num_vertices ({expected})"
                )"""

        uvs_arr = cls._to_float32_flat_or_none(uvs, "uvs")
        if uvs_arr is not None and len(uvs_arr) // 2 != vertex_count:
            raise ValueError("uvs length must be 2 * vertex_count (if provided)")

        cbo_arr = cls._to_float32_flat_or_none(colors, "colors")

        if cbo_arr is None:
            if color_per_vertex is not None:
                # user supplied a colour-per-vertex function or preset
                # If color_per_vertex is a scalar (same colour for all), broadcast accordingly
                if isinstance(color_per_vertex, (list, tuple, np.ndarray)):
                    colors = np.asarray(color_per_vertex, dtype=np.float32).reshape(-1)
                    if len(colors) == 3:
                        # single colour; replicate per vertex
                        cbo_arr = np.tile(colors, vertex_count)
                    elif len(colors) == vertex_count * 3:
                        cbo_arr = colors
                    else:
                        raise ValueError("color_per_vertex array length invalid")
                else:
                    raise ValueError("color_per_vertex must be array-like or None")
            else:
                # default per-vertex colour (red)
                cbo_arr = cls._default_colors_for_vertices(vertex_count)
        # If cbo_arr still None and we had color_per_vertex, ensure it's flat
        if cbo_arr is not None and cbo_arr.ndim != 1:
            cbo_arr = cbo_arr.reshape(-1)

        # Indices (optional)
        indices_arr = cls._to_int32_flat(indices, "indices", required=False)

        return cls(vbo=vbo, nbo=nbo, uvs=uvs_arr, cbo=cbo_arr, ebo=indices_arr)

    def draw(
        self,
        color: tuple = None,
        line_width: float = 1.0,
        mode: int = GL.GL_TRIANGLES,
        fill: bool = False,
        alpha: float = 1.0,
    ):
        """
        Draw the mesh with optional colour override and transparency.

        Args:
            color: Optional colour override. If None and vertex colors exist, uses vertex colors.
            line_width: Line width for wireframe mode
            mode: OpenGL drawing mode
            fill: Whether to fill or use wireframe
            alpha: Transparency value from 0.0 (opaque) to 1.0 (fully transparent)
        """
        if fill:
            fill_mode = GL.GL_FILL
        else:
            fill_mode = GL.GL_LINE

        # Set material properties for the isosurface
        GL.glLineWidth(line_width)

        # Enable alpha blending for transparency
        if alpha < 1.0:
            GL.gl_enable(GL.GL_BLEND)
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        else:
            GL.glDisable(GL.GL_BLEND)

        # Check if we should use vertex colors or override colour
        if color is None and self.cbo is not None:
            # Use vertex colors (for fo-fc maps)
            GL.gl_enableClientState(GL.GL_COLOR_ARRAY)
            GL.glColorPointer(3, GL.GL_FLOAT, 0, self.cbo)
            # Note: Alpha blending for vertex colors would require 4-component colors
            # For now, we'll use the alpha value for the overall transparency
        else:
            # Use override colour
            if color is None:
                color = (0.0, 0.0, 1.0)  # Default blue
            # Use glColor4f to include alpha value
            GL.glColor4f(color[0], color[1], color[2], 1.0 - alpha)

        # Draw as wireframe for better visibility
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, fill_mode)

        # Draw the mesh
        GL.glDrawElements(mode, len(self.ebo) * 3, GL.GL_UNSIGNED_INT, self.ebo)

        # Restore fill mode
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        # Clean up colour array state if we used it
        if color is None and self.cbo is not None:
            GL.glDisableClientState(GL.GL_COLOR_ARRAY)
