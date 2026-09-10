"""
Provides functionality for managing OpenGL mesh data, including vertices, normals,
texture coordinates, colors, and indices. This class offers a set of utilities to
handle OpenGL-related state objects and simplify rendering workflows.
"""

from typing import Any, Optional, Union

import numpy as np
from decologr import Decologr as log
from numpy import dtype, generic, ndarray

from picogl.backend.gl.api import (
    gl_disable_legacy_client_state,
    gl_draw_elements,
    gl_enable_legacy_client_state,
)
from picogl.backend.gl.api.blending import gl_blend_func
from picogl.backend.gl.api.color import gl_color_4f
from picogl.backend.gl.api.line import gl_line_width
from picogl.backend.gl.api.pointer import (
    gl_color_array_pointer,
    gl_normal_array_pointer,
    gl_texcoord_array_pointer,
    gl_vertex_array_pointer,
)
from picogl.backend.gl.api.polygon_mode import gl_polygon_mode
from picogl.backend.gl.capability import GLBlendFactor, GLPipelineCapability
from picogl.backend.gl.enums import GLDrawMode, GLIndexType, GLNumeric
from picogl.backend.gl.legacy.setup_vbg import VertexBufferGroup, setup_vbg
from picogl.backend.gl.state.client import GLClientState
from picogl.backend.gl.state.fill import GLFillMode
from picogl.core.rgbcolor import RGBColor
from picogl.gpu.buffers.attributes import CanonicalVertexAttrs
from picogl.gpu.buffers.factory.validation import validate_input_data
from picogl.gpu.buffers.helper import as_vec3_array
from picogl.gpu.buffers.vertex.vbo.vbo_class import VBOType
from picogl.renderer.draw_spec import (
    MeshDrawInfo,
    MeshDrawSpec,
    compute_draw_spec,
    execute_draw_spec,
    infer_draw_info,
)
from picogl.utils.loader.object_data import ObjectData


class MeshData:
    """
    Representation of mesh data for OpenGL rendering.

    This class encapsulates mesh data and provides utilities for setting up and
    managing vertex attributes such as positions, normals, texture coordinates,
    colors, and indices. It enables interoperability with OpenGL through context
    management and binding/unbinding functions. Additionally, the class includes
    methods for raw data conversion and generation of default attributes.

    Attributes:
        vertices: Optional array of vertex positions as np.ndarray.
        normals: Optional array of vertex normals as np.ndarray.
        texcoords: Optional array of texture coordinates as np.ndarray.
        colors: Optional array of vertex colors as np.ndarray.
        indices: Optional array of vertex indices as np.ndarray.
        vertex_count: Optional count of vertices, computed from vertices input.
        draw_info: CPU draw layout (mode, indexed, per-item strides).
        item_keys: Optional ``(N, K)`` identity table for logical items.
        color_source_indices: Optional per-vertex gather indices into a
            logical color array.

    Methods:
        bind:
            Binds vertex attributes to OpenGL client states for rendering.
        unbind:
            Unbinds vertex attributes from OpenGL client states.
        as_canonical_names:
            Converts the mesh data into a dictionary with canonical attribute names.
        draw:
            Draws the mesh with optional OpenGL parameters for color, line width,
            draw mode, fill mode, and alpha transparency.
        from_raw:
            Class method for constructing a MeshData object from raw input data.
    """

    def __init__(
        self,
        vertices: np.ndarray = None,
        normals: np.ndarray = None,
        texcoords: np.ndarray = None,
        colors: np.ndarray = None,
        indices: np.ndarray = None,
        draw_info: MeshDrawInfo | None = None,
        item_keys: np.ndarray | None = None,
        color_source_indices: np.ndarray | None = None,
    ):
        """Store CPU mesh arrays and draw layout (no GL objects)."""
        self.vertices = self._ensure_xyz(vertices)
        n = self._xyz_row_count(self.vertices)

        self.normals = self._ensure_xyz(normals, n)
        self.colors = self._ensure_xyz(colors, n)
        self.texcoords = texcoords
        self.indices = indices
        self.item_keys = item_keys
        self.color_source_indices = color_source_indices
        self.vao = None

        self.vertex_count = (
            len(np.asarray(vertices, dtype=np.float32).flatten()) // 3
            if vertices is not None
            else None
        )
        if draw_info is not None:
            self.draw_info = draw_info
        else:
            indices_arr = self.normalized_indices
            index_count = 0 if indices_arr is None else int(indices_arr.size)
            self.draw_info = infer_draw_info(
                has_indices=indices_arr is not None,
                index_count=index_count,
            )

    @property
    def normalized_indices(self) -> ndarray[Any, dtype[Any]] | None:
        """
        normalized indices
        """
        if self.indices is None:
            return None

        indices = np.asarray(self.indices)
        if indices.size == 0:
            return None

        return indices.astype(np.uint32).ravel()

    def resolved_draw_info(self) -> MeshDrawInfo:
        """Return the mesh draw layout (always set in ``__init__``)."""
        return self.draw_info

    def draw_spec(
        self,
        item_count: int | None = None,
        first_item: int = 0,
    ) -> MeshDrawSpec:
        """Build a GL-free draw for ``first_item`` .. ``first_item + item_count``.

        When :attr:`MeshDrawInfo.elements_per_item` is set, ``first_item`` is a
        logical item index (atom, bond, …) and is converted to an index range.

        :param item_count: Number of items to draw; ``None`` draws the remainder.
        :param first_item: First logical item (or first index/vertex if unstrided).
        :return: :class:`MeshDrawSpec` clamped to the mesh buffers.
        """
        info = self.resolved_draw_info()
        indices = self.normalized_indices
        index_count = 0 if indices is None else int(indices.size)
        vertex_count = int(self._xyz_row_count(self.vertices))
        return compute_draw_spec(
            info,
            index_count=index_count,
            vertex_count=vertex_count,
            first_item=first_item,
            item_count=item_count,
        )

    def expand_attribute_per_item(
        self,
        values: np.ndarray,
        elements_per_item: int | None = None,
    ) -> np.ndarray:
        """Repeat one row per item across ``elements_per_item`` vertices.

        :param values: Array of shape ``(N, 3)`` (one row per logical item).
        :param elements_per_item: Repeat count; defaults to
            :attr:`MeshDrawInfo.vertices_per_item`.
        :return: float32 array of shape ``(N * count, 3)``.
        """
        rows = np.asarray(values, dtype=np.float32).reshape(-1, 3)
        count = elements_per_item
        if count is None:
            count = self.draw_info.vertices_per_item
        if count is None or int(count) <= 1:
            return rows
        return np.repeat(rows[:, None, :], int(count), axis=1).reshape(-1, 3)

    def expand_colors(self, logical_colors: np.ndarray) -> np.ndarray:
        """Expand per-item or per-source colors to one RGB row per vertex.

        If ``logical_colors`` already matches the vertex count it is returned
        unchanged. Otherwise :attr:`color_source_indices` (gather) or
        :meth:`expand_attribute_per_item` is applied.

        :param logical_colors: RGB rows (vertices, items, or gather sources).
        :return: float32 array of shape ``(V, 3)``.
        """
        colors = np.asarray(logical_colors, dtype=np.float32).reshape(-1, 3)
        n_verts = int(self._xyz_row_count(self.vertices))
        if 0 < n_verts == colors.shape[0]:
            return colors
        src = self.color_source_indices
        if src is not None:
            return colors[np.asarray(src, dtype=np.intp)]
        return self.expand_attribute_per_item(colors)

    def apply_logical_colors(self, logical_colors: np.ndarray) -> np.ndarray:
        """Expand logical colors onto :attr:`colors` (CPU only; no GPU upload).

        :param logical_colors: RGB rows (vertices, items, or gather sources).
        :return: The expanded per-vertex color array now stored on this mesh.
        """
        self.colors = self.expand_colors(logical_colors)
        return self.colors

    def attach_vao(self, vao: Any) -> Any:
        """Bind *vao* to this mesh and this mesh to *vao* (bidirectional).

        :param vao: GPU vertex array / buffer group that will issue ``glDraw*``.
        :return: *vao* (for call chaining from setup helpers).
        """
        self.vao = vao
        if vao is not None:
            vao.mesh = self
        return vao

    def draw(
        self,
        *,
        first_item: int = 0,
        item_count: int | None = None,
        count: int | None = None,
    ) -> None:
        """Issue a modern ``glDraw*`` via the attached VAO and :meth:`draw_spec`.

        :param first_item: First logical item (atom, bond, …).
        :param item_count: Number of items; ``None`` draws the remainder.
        :param count: Override element/vertex count (HETATM temporary EBO).
        :raises RuntimeError: When no VAO has been attached.
        """
        vao = self.vao
        if vao is None:
            raise RuntimeError("MeshData is not associated with a VAO")
        spec = self.draw_spec(first_item=first_item, item_count=item_count)
        if count is not None:
            spec = MeshDrawSpec(
                mode=spec.mode,
                count=int(count),
                first=0,
                pointer=0,
            )
        execute_draw_spec(vao, spec)

    def validate(self):
        """validate mesh data"""
        validate_input_data(
            vertices=self.vertices,
            indices=self.indices,
            normals=self.normals,
            colors=self.colors,
        )

    def setup_atom_vao(self):
        """Build a vertex array from atom mesh data (layout included)."""
        from elmo.gl.backend.modern.entities.atoms.setup import (
            setup_atom_vao as _setup_atom_vao,
        )

        return _setup_atom_vao(self)

    def setup_ribbon_vao(self):
        from elmo.gl.backend.modern.primitives.ribbon.setup import (
            setup_ribbon_vao as _setup_ribbon_vao,
        )

        return _setup_ribbon_vao(self)

    def setup_calpha_vao(self):
        from elmo.gl.backend.modern.entities.calpha.setup_buffers import (
            setup_calpha_vao as _setup_calpha_vao,
        )

        return _setup_calpha_vao(self)

    def setup_bond_vao(self):
        """Build a vertex array from bond mesh data (layout included)."""
        from elmo.gl.backend.modern.entities.bonds.setup import (
            setup_bond_vao as _setup_bond_vao,
        )

        return _setup_bond_vao(self)

    def setup_vertex_attributes(self):
        """setup vertex attributes"""
        from picogl.backend.modern.core.vertex.attribute import VertexAttribute

        vertex_attributes = [
            VertexAttribute(0, self.normalized_vertices, VBOType.VBO),
            VertexAttribute(1, self.normalized_colors, VBOType.CBO),
            VertexAttribute(2, self.normalized_normals, VBOType.NBO),
        ]
        return vertex_attributes

    @property
    def normalized_normals(self) -> ndarray[Any, dtype[generic]]:
        return as_vec3_array(self.normals)

    @property
    def normalized_colors(self) -> ndarray[Any, dtype[generic]]:
        return as_vec3_array(self.colors)

    @property
    def normalized_vertices(self) -> ndarray[Any, dtype[generic]]:
        return as_vec3_array(self.vertices)

    @staticmethod
    def _ensure_xyz(arr, n=None):
        if arr is None:
            if n is None:
                return None
            return np.zeros((n, 3), dtype=np.float32)

        a = np.asarray(arr, dtype=np.float32).reshape(-1, 3)

        if n is not None and a.shape[0] != n:
            raise ValueError("Attribute length mismatch")

        return a

    # ---- Backward compatibility aliases ----

    def extend(self, vertices=None, normals=None, colors=None, uvs=None):
        if vertices is not None:
            vertices = np.asarray(vertices, dtype=np.float32)
            self.vertices = (
                vertices
                if self.vertices is None
                else np.vstack([self.vertices, vertices])
            )

        if normals is not None:
            normals = np.asarray(normals, dtype=np.float32)
            self.normals = (
                normals if self.normals is None else np.vstack([self.normals, normals])
            )

        if colors is not None:
            colors = np.asarray(colors, dtype=np.float32)
            self.colors = (
                colors if self.colors is None else np.vstack([self.colors, colors])
            )

        if uvs is not None:
            uvs = np.asarray(uvs, dtype=np.float32)
            self.uvs = uvs if self.uvs is None else np.vstack([self.uvs, uvs])

    def setup_vbg(
        self, draw_mode: int | GLDrawMode = GLDrawMode.TRIANGLE_STRIP
    ) -> VertexBufferGroup:
        from picogl.gpu.buffers.helper import as_vec3_array

        return setup_vbg(
            colors=self.normalized_colors,
            normals=self.normalized_normals,
            positions=self.normalized_vertices,
            draw_mode=draw_mode,
        )

    @staticmethod
    def from_object_data(object_data: ObjectData) -> "MeshData":
        data: MeshData = MeshData.from_raw(
            vertices=object_data.vertices,
            normals=object_data.normals,
            colors=object_data.generate_solid_color(color=RGBColor.RED),
        )
        return data

    def extend_from_mesh(self, other: "MeshData"):
        self.extend(
            vertices=other.vertices,
            normals=other.normals,
            colors=other.colors,
            uvs=other.uvs,
        )

    # VBO → vertices
    @property
    def vbo(self):
        return self.vertices

    @vbo.setter
    def vbo(self, value):
        self.vertices = value

    # NBO → normals
    @property
    def nbo(self):
        return self.normals

    @nbo.setter
    def nbo(self, value):
        self.normals = value

    # UVs → texcoords
    @property
    def uvs(self):
        return self.texcoords

    @uvs.setter
    def uvs(self, value):
        self.texcoords = value

    # CBO → colors
    @property
    def cbo(self):
        return self.colors

    @cbo.setter
    def cbo(self, value):
        self.colors = value

    # EBO → indices
    @property
    def ebo(self):
        return self.indices

    @ebo.setter
    def ebo(self, value):
        self.indices = value

    def as_canonical_names(self) -> dict:
        """Convert into canonical names."""
        return {
            CanonicalVertexAttrs.POSITIONS: self.vertices,
            CanonicalVertexAttrs.COLORS: self.colors,
            CanonicalVertexAttrs.NORMALS: self.normals,
            CanonicalVertexAttrs.INDICES: self.indices,
        }

    def __str__(self):
        return f"{self.vertices} {self.texcoords} {self.colors} "

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
        """Simple default: red colour per vertex"""
        colors = np.tile(np.array([1.0, 0.0, 0.0], dtype=np.float32), (vertex_count, 1))
        return colors.reshape(-1)

    @classmethod
    def _default_normals_for_vertices(cls, vertex_count: int) -> np.ndarray:
        """Simple default: simple normal per vertex"""
        normals = np.tile([0.0, 0.0, 1.0], (vertex_count, 1)).astype(np.float32)
        return normals.reshape(-1)

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        if self.vertices is not None:
            gl_enable_legacy_client_state(GLClientState.VERTEX)
            gl_vertex_array_pointer(
                pointer=self.vertices, size=3, num_type=GLNumeric.FLOAT
            )
        if self.normals is not None:
            gl_enable_legacy_client_state(GLClientState.NORMAL)
            gl_normal_array_pointer(pointer=self.normals, num_type=GLNumeric.FLOAT)
        if self.colors is not None:
            gl_enable_legacy_client_state(GLClientState.COLOR)
            gl_color_array_pointer(
                pointer=self.colors, size=3, num_type=GLNumeric.FLOAT
            )
        if self.texcoords is not None:
            gl_enable_legacy_client_state(GLClientState.TEXCOORD)
            gl_texcoord_array_pointer(
                pointer=self.texcoords, size=2, num_type=GLNumeric.FLOAT
            )

    def unbind(self):
        if self.texcoords is not None:
            gl_disable_legacy_client_state(GLClientState.TEXCOORD)
        if self.colors is not None:
            gl_disable_legacy_client_state(GLClientState.COLOR)
        if self.normals is not None:
            gl_disable_legacy_client_state(GLClientState.NORMAL)
        if self.vertices is not None:
            gl_disable_legacy_client_state(GLClientState.VERTEX)

    @classmethod
    def from_raw(
        cls,
        vertices: Union[np.ndarray, list[float]],
        normals: Optional[Union[np.ndarray, list[float]]] = None,
        uvs: Optional[Union[np.ndarray, list[float]]] = None,
        colors: Optional[Union[np.ndarray, list[float], list[tuple | int]]] = None,
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

        if normals is None:
            normals = np.zeros((vertex_count, 3), dtype=np.float32)

        nbo = cls._to_float32_flat_or_none(normals, "normals")
        if nbo is not None and len(nbo) // 3 != vertex_count:
            raise ValueError("normals length must be 3 * vertex_count (if provided)")

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

        return cls(
            vertices=vbo,
            normals=nbo,
            texcoords=uvs_arr,
            colors=cbo_arr,
            indices=indices_arr,
        )

    def draw_legacy(
        self,
        color: tuple | None = None,
        line_width: float = 1.0,
        mode: int = GLDrawMode.TRIANGLES,
        fill: bool = False,
        alpha: float = 1.0,
    ):
        """Draw with legacy client arrays (``gl*Pointer`` + ``glDrawElements``).

        :param color: Optional RGB override. If ``None`` and vertex colors exist,
            uses the colour array.
        :param line_width: Line width for wireframe mode.
        :param mode: OpenGL draw mode.
        :param fill: Whether to fill polygons or use wireframe.
        :param alpha: Transparency (0.0 opaque … 1.0 fully transparent).
        """
        # Safety checks to prevent segfaults
        if self.vertices is None:
            print("Warning: Cannot draw mesh - no vertex data (vertices)")
            return

        if self.indices is None:
            print("Warning: Cannot draw mesh - no element data (ebo)")
            return

        if len(self.indices) == 0:
            print("Warning: Cannot draw mesh - empty element buffer")
            return

        # Validate ebo data to prevent segfaults
        if self.indices.dtype != np.uint32 and self.indices.dtype != np.int32:
            print(
                f"Warning: Invalid ebo dtype {self.indices.dtype}, converting to uint32"
            )
            self.indices = self.indices.astype(np.uint32)

        # Check for invalid indices that could cause segfaults
        max_vertex_index = len(self.vertices) // 3 - 1
        if np.any(self.indices > max_vertex_index):
            print(f"Warning: Invalid vertex indices in ebo (max: {max_vertex_index})")
            # Clamp indices to valid range
            self.indices = np.clip(self.indices, 0, max_vertex_index)

        if np.any(self.indices < 0):
            print("Warning: Negative vertex indices in ebo")
            # Set negative indices to 0
            self.indices = np.maximum(self.indices, 0)

        if fill:
            fill_mode = GLFillMode.FILL
        else:
            fill_mode = GLFillMode.LINE

        # Set material properties for the isosurface
        gl_line_width(line_width)

        # Enable alpha blending for transparency
        if alpha < 1.0:
            gl_enable(GLPipelineCapability.BLEND)
            gl_blend_func(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)
        else:
            gl_disable(GLPipelineCapability.BLEND)

        # Check if we should use vertex colors or override colour
        if color is None and self.colors is not None:
            # Use vertex colors (for fo-fc maps)
            gl_enable_legacy_client_state(GLClientState.COLOR)
            gl_color_array_pointer(
                pointer=self.colors, size=3, num_type=GLNumeric.FLOAT
            )
            # Note: Alpha blending for vertex colors would require 4-component colors
            # For now, we'll use the alpha value for the overall transparency
        else:
            # Use override colour
            if color is None:
                color = (0.0, 0.0, 1.0)  # Default blue
            # Use glColor4f to include alpha value
            gl_color_4f(color[0], color[1], color[2], 1.0 - alpha)

        # Draw as wireframe for better visibility
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, fill_mode)

        try:
            # Draw the mesh with additional safety checks
            element_count = len(self.indices)
            if element_count > 0:
                gl_draw_elements(
                    element_count,
                    GLIndexType.UNSIGNED_INT,
                    mode,
                    pointer=self.indices,
                )
        except Exception as e:
            log.error(f"Error in glDrawElements: {e}")
            log.error(f"Element count: {element_count}")
            log.error(f"EBO dtype: {self.indices.dtype}")
            log.error(f"EBO shape: {self.indices.shape}")
            log.error(
                f"VBO length: {len(self.vertices) if self.vertices is not None else 'None'}"
            )

        # Restore fill mode
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)

        # Clean up colour array state if we used it
        if color is None and self.colors is not None:
            gl_disable_legacy_client_state(GLClientState.COLOR)

    def delete(self):
        """Drop CPU references to mesh arrays (no gl objects on this type)."""
        # Use ``is not None`` — nbo/cbo/ebo are often numpy arrays; ``if arr:`` is ambiguous.
        if self.normals is not None:
            self.normals = None
        if self.colors is not None:
            self.colors = None
        if self.indices is not None:
            self.indices = None
        if self.vertices is not None:
            self.vertices = None
        if self.texcoords is not None:
            self.texcoords = None

    @staticmethod
    def _xyz_row_count(arr: Optional[np.ndarray]) -> int:
        if arr is None:
            return 0
        a = np.asarray(arr)
        if a.size == 0:
            return 0
        if a.ndim == 2 and a.shape[-1] == 3:
            return int(a.shape[0])
        return int(a.size // 3)

    @staticmethod
    def _as_xyz_f32(
        arr: Optional[np.ndarray],
        n: int,
        name: str,
    ) -> np.ndarray:
        """Return (n, 3) float32; ``None`` becomes zeros."""
        if arr is None:
            return np.zeros((n, 3), dtype=np.float32)
        out = np.asarray(arr, dtype=np.float32).reshape(-1, 3)
        if out.shape[0] != n:
            raise ValueError(f"{name} length {out.shape[0]} != vertex count {n}")
        return out

    @staticmethod
    def _as_uv_f32(arr: Optional[np.ndarray], n: int) -> np.ndarray:
        """Return (n, 2) float32; ``None`` becomes zeros."""
        if arr is None:
            return np.zeros((n, 2), dtype=np.float32)
        out = np.asarray(arr, dtype=np.float32).reshape(-1, 2)
        if out.shape[0] != n:
            raise ValueError(f"texcoords length {out.shape[0]} != vertex count {n}")
        return out

    @staticmethod
    def _indices_u32_flat(indices: Optional[np.ndarray]) -> Optional[np.ndarray]:
        if indices is None:
            return None
        return np.asarray(indices, dtype=np.uint32).reshape(-1)

    def append_mesh(self, mesh: "MeshData") -> None:
        """
        Concatenate ``mesh`` after this mesh: vertices/normals/colors/uvs are stacked;
        triangle indices from ``mesh`` are offset by the current vertex count.

        Invariants:
            * Vertices are (N, 3), float32.
            * Normals and colors, if present on either mesh, are expanded to (N, 3) with
              zeros for missing rows so lengths match vertices.
            * Indices are uint32 element buffer; merged as ``concat(self, mesh + base)``.
            * Optional texcoords (N, 2); if either side has them, both sides are padded.

        :param mesh: Another :class:`MeshData` instance (same attribute layout).
        """
        if mesh is None:
            raise TypeError("append_mesh: mesh must not be None")

        if mesh.colors is None:
            raise ValueError("append_mesh: incoming mesh must have colors")

        mv = mesh.vertices
        if mv is None:
            return

        m_count = self._xyz_row_count(mv)
        if m_count == 0:
            return

        mv3 = np.asarray(mv, dtype=np.float32).reshape(-1, 3)

        # --- Empty receiver: copy mesh wholesale ---
        if self.vertices is None:
            self.vertices = mv3.copy()
            self.normals = self._as_xyz_f32(mesh.normals, m_count, "normals")
            self.colors = self._as_xyz_f32(mesh.colors, m_count, "colors")
            mi = self._indices_u32_flat(mesh.indices)
            self.indices = None if mi is None else mi.copy()
            want_uv = mesh.texcoords is not None
            self.texcoords = (
                self._as_uv_f32(mesh.texcoords, m_count) if want_uv else None
            )
            self.vertex_count = m_count
            return

        sv3 = np.asarray(self.vertices, dtype=np.float32).reshape(-1, 3)
        s_count = sv3.shape[0]

        si = self._indices_u32_flat(self.indices)
        mi = self._indices_u32_flat(mesh.indices)
        if si is None:
            raise ValueError(
                "append_mesh: base mesh has vertices but no indices (cannot merge)"
            )
        if mi is None:
            raise ValueError(
                "append_mesh: appended mesh has vertices but no indices (cannot merge)"
            )

        base = np.uint32(s_count)
        mn = self._as_xyz_f32(mesh.normals, m_count, "normals")
        mc = self._as_xyz_f32(mesh.colors, m_count, "colors")
        sn = self._as_xyz_f32(self.normals, s_count, "normals")
        sc = self._as_xyz_f32(self.colors, s_count, "colors")

        want_uv = (self.texcoords is not None) or (mesh.texcoords is not None)
        if want_uv:
            st = self._as_uv_f32(self.texcoords, s_count)
            mt = self._as_uv_f32(mesh.texcoords, m_count)
            self.texcoords = np.vstack([st, mt])
        else:
            self.texcoords = None

        self.vertices = np.vstack([sv3, mv3])
        self.normals = np.vstack([sn, mn])
        self.colors = np.vstack([sc, mc])

        mi_shift = mi.astype(np.uint64) + np.uint64(base)
        self.indices = np.concatenate([si.astype(np.uint64), mi_shift]).astype(
            np.uint32
        )
        self.vertex_count = int(self.vertices.shape[0])
