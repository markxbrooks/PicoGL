"""
Mesh Data
"""
from typing import Optional, Union

import numpy as np
from decologr import Decologr as log
from OpenGL import GL
from OpenGL.GL import glDrawElements
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays
from OpenGL.raw.GL.VERSION.GL_3_0 import glBindVertexArray

from picogl.attrs.context_manager import ContextManagerAttrs
from picogl.attrs.vertex import CanonicalVertexAttrs
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.backend.modern.core.vertex.buffer.object import ModernVBO
from picogl.buffers.base import VertexBase
from picogl.buffers.vertex.vbo.vbo_class import VBOType
from picogl.mode import GLMode
from picogl.protocols.drawable_buffer import DrawableBuffer


class MeshData:
    """Holds OpenGL-related state objects for rendering."""

    def __init__(
        self,
        vertices: np.ndarray = None,
        normals: np.ndarray = None,
        texcoords: np.ndarray = None,
        colors: np.ndarray = None,
        indices: np.ndarray = None,
    ):
        """set up the OpenGL context"""
        self.vbo = vertices
        self.normals = normals
        self.texcoords = texcoords
        self.cbo = colors
        self.indices = indices

        self.vertex_count = (
            len(np.asarray(vertices, dtype=np.float32).flatten()) // 3
            if vertices is not None
            else None
        )

    def as_canonical_names(self) -> dict:
        """Convert into canonical names."""
        return {
            CanonicalVertexAttrs.POSITIONS: self.vbo,
            CanonicalVertexAttrs.COLORS: self.cbo,
            CanonicalVertexAttrs.NORMALS: self.normals,
            CanonicalVertexAttrs.INDICES: self.indices,
        }

    def __str__(self):
        return f"{self.vbo} {self.texcoords} {self.cbo} "

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
            GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
            GL.glVertexPointer(3, GL.GL_FLOAT, 0, self.vbo)
        if self.normals is not None:
            GL.glEnableClientState(GL.GL_NORMAL_ARRAY)
            GL.glNormalPointer(GL.GL_FLOAT, 0, self.normals)
        if self.cbo is not None:
            GL.glEnableClientState(GL.GL_COLOR_ARRAY)
            GL.glColorPointer(3, GL.GL_FLOAT, 0, self.cbo)
        if self.texcoords is not None:
            GL.glEnableClientState(GL.GL_TEXTURE_COORD_ARRAY)
            GL.glTexCoordPointer(2, GL.GL_FLOAT, 0, self.texcoords)

    def unbind(self):
        if self.texcoords is not None:
            GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        if self.cbo is not None:
            GL.glDisableClientState(GL.GL_COLOR_ARRAY)
        if self.normals is not None:
            GL.glDisableClientState(GL.GL_NORMAL_ARRAY)
        if self.vbo is not None:
            GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

    @classmethod
    def from_raw(
            cls,
            vertices: Union[np.ndarray, list[float]],
            normals: Optional[Union[np.ndarray, list[float]]] = None,
            uvs: Optional[Union[np.ndarray, list[float]]] = None,
            colors: Optional[Union[np.ndarray, list[float]]] = None,
            indices: Optional[Union[np.ndarray, list[float]]] = None,
            color_per_vertex: Optional[Union[np.ndarray, list[float]]] = None,
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
            normals = np.zeros((num_vertices, 3), dtype=np.float32)

        nbo = cls._to_float32_flat_or_none(normals, "normals")

        if nbo is not None:
            expected = num_vertices * 3

        uvs_arr = cls._to_float32_flat_or_none(uvs, VBOType.UVS)
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

        return cls(vertices=vbo, normals=nbo, texcoords=uvs_arr, colors=cbo_arr, indices=indices_arr)

    def draw(
        self,
        color: tuple = None,
        line_width: float = 1.0,
        mode: int = GL.GL_TRIANGLES,
        fill: bool = False,
        alpha: float = 1.0,
    ):
        """
        Draw the mesh with optional color override and transparency.

        Args:
            color: Optional color override. If None and vertex colors exist, uses vertex colors.
            line_width: Line width for wireframe mode
            mode: OpenGL drawing mode
            fill: Whether to fill or use wireframe
            alpha: Transparency value from 0.0 (opaque) to 1.0 (fully transparent)
        """
        # Safety checks to prevent segfaults
        if self.vbo is None:
            print("Warning: Cannot draw mesh - no vertex data (vbo)")
            return
        
        if self.indices is None:
            print("Warning: Cannot draw mesh - no element data (ebo)")
            return
            
        if len(self.indices) == 0:
            print("Warning: Cannot draw mesh - empty element buffer")
            return
            
        # Validate ebo data to prevent segfaults
        if self.indices.dtype != np.uint32 and self.indices.dtype != np.int32:
            print(f"Warning: Invalid ebo dtype {self.indices.dtype}, converting to uint32")
            self.indices = self.indices.astype(np.uint32)
            
        # Check for invalid indices that could cause segfaults
        max_vertex_index = len(self.vbo) // 3 - 1
        if np.any(self.indices > max_vertex_index):
            print(f"Warning: Invalid vertex indices in ebo (max: {max_vertex_index})")
            # Clamp indices to valid range
            self.indices = np.clip(self.indices, 0, max_vertex_index)
            
        if np.any(self.indices < 0):
            print("Warning: Negative vertex indices in ebo")
            # Set negative indices to 0
            self.indices = np.maximum(self.indices, 0)

        if fill:
            fill_mode = GL.GL_FILL
        else:
            fill_mode = GL.GL_LINE

        # Set material properties for the isosurface
        GL.glLineWidth(line_width)

        # Enable alpha blending for transparency
        if alpha < 1.0:
            GL.glEnable(GL.GL_BLEND)
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        else:
            GL.glDisable(GL.GL_BLEND)

        # Check if we should use vertex colors or override colour
        if color is None and self.cbo is not None:
            # Use vertex colors (for fo-fc maps)
            GL.glEnableClientState(GL.GL_COLOR_ARRAY)
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

        try:
            # Draw the mesh with additional safety checks
            element_count = len(self.indices)
            if element_count > 0:
                GL.glDrawElements(mode, element_count, GL.GL_UNSIGNED_INT, self.indices)
        except Exception as e:
            log.error(f"Error in glDrawElements: {e}")
            log.error(f"Element count: {element_count}")
            log.error(f"EBO dtype: {self.indices.dtype}")
            log.error(f"EBO shape: {self.indices.shape}")
            log.error(f"VBO length: {len(self.vbo) if self.vbo is not None else 'None'}")

        # Restore fill mode
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        # Clean up colour array state if we used it
        if color is None and self.cbo is not None:
            GL.glDisableClientState(GL.GL_COLOR_ARRAY)

    def delete(self):
        """Drop CPU references to mesh arrays (no GL objects on this type)."""
        # Use ``is not None`` — nbo/cbo/ebo are often numpy arrays; ``if arr:`` is ambiguous.
        if self.normals is not None:
            self.normals = None
        if self.cbo is not None:
            self.cbo = None
        if self.indices is not None:
            self.indices = None
        if self.vbo is not None:
            self.vbo = None
        if self.texcoords is not None:
            self.texcoords = None


class MeshDataModern(VertexBase):
    """Holds OpenGL-related state objects for rendering."""

    def __init__(self, vao: Optional[Union[VertexArrayObject, DrawableBuffer]] = None, vbo: Optional[ModernVBO] = None,
                 nbo: Optional[ModernVBO] = None, uvs: Optional[ModernVBO] = None, ebo: Optional[ModernVBO] = None,
                 cbo: Optional[ModernVBO] = None, index_count: Optional[int] = None,
                 vertex_count: Optional[int] = None):
        """set up the OpenGL context"""
        super().__init__()
        self.vao = vao
        self.vbo = vbo
        self.nbo = nbo
        self.uvs = uvs
        self.cbo = cbo
        self.ebo = ebo
        self.index_count = index_count
        self.vertex_count = vertex_count

        # Enforce correctness
        if self.ebo is not None:
            if self.index_count is None:
                raise ValueError("index_count required when using EBO")
        else:
            if self.vertex_count is None:
                raise ValueError("vertex_count required when no EBO is present")

    def delete(self):
        for buf in (self.nbo, self.ebo, self.cbo, self.vbo, self.uvs):
            if buf is not None:
                buf.delete()

        if hasattr(self.vao, "delete"):
            self.vao.delete()

        self.vao = None
        self.vbo = None
        self.nbo = None
        self.ebo = None
        self.cbo = None
        self.uvs = None

    def draw(
            self,
            indices: int = None,
            mvp_matrix: np.ndarray = None,
            shader_type: str = None,
            mode=GL_TRIANGLES
    ):
        """Draw the bond buffers using OpenGL"""
        try:
            # High-level path (preferred if present)
            if isinstance(self.vao, DrawableBuffer):
                self.vao.draw()
                return

            # Standard VAO path
            if self.vao is not None:
                self.bind()

            if self.ebo is not None:
                glDrawElements(mode, self.index_count, GL_UNSIGNED_INT, None)
            else:
                glDrawArrays(mode, 0, self.vertex_count)

            if self.vao is not None:
                self.unbind()

        except Exception as ex:
            log.error(f"Error drawing mesh: {ex}", scope=self.__class__.__name__)

    def bind(self):
        if hasattr(self.vao, ContextManagerAttrs.BIND):
            self.vao.bind()
        else:
            glBindVertexArray(self.vao)

    def unbind(self):
        glBindVertexArray(0)

    def configure(self):
        pass


class MeshDataTest:
    """Mesh Data"""

    mesh_data_classes = {
        GLMode.LEGACY: MeshData,
        GLMode.MODERN: MeshDataModern,
    }

    def __init__(self, gl_mode: GLMode = GLMode.LEGACY, **kwargs):
        self.gl_mode = gl_mode

        impl_cls = self.mesh_data_classes.get(gl_mode)
        if impl_cls is None:
            raise ValueError(f"Unsupported GLMode: {gl_mode}")

        self.impl = impl_cls(**kwargs)

    @classmethod
    def from_raw(cls, gl_mode: GLMode, **kwargs):
        impl_cls = self.mesh_data_classes.get(gl_mode)
        if impl_cls is None:
            raise ValueError(f"Unsupported GLMode: {gl_mode}")

        impl = impl_cls.from_raw(**kwargs)
        obj = cls(gl_mode)
        obj.impl = impl
        return obj

    def draw(self, *args, **kwargs):
        return self.impl.draw(*args, **kwargs)

    def bind(self):
        if hasattr(self.impl, ContextManagerAttrs.BIND):
            return self.impl.bind()

    def unbind(self):
        if hasattr(self.impl, ContextManagerAttrs.UNBIND):
            return self.impl.unbind()