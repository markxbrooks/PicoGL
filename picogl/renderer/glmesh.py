"""
A module for GPU-resident indexed and non-indexed geometry.

This module defines the `GLMesh` class, which represents a 3D mesh stored on the
GPU. It provides mechanisms for defining a mesh's vertices, faces, colors, normals,
UVs, and vertex layout, along with functionality for uploading these attributes to
GPU buffers and expanding indexed meshes into per-triangle vertex lists if needed.
"""

import ctypes
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

import numpy as np
from elmo.glsl.layouts import build_shader_layouts
from numpy import dtype, floating, generic, ndarray
from numpy._typing import _64Bit

from picogl.backend.gl.api.glcleanup import gl_release_vertex_array_object
from picogl.backend.gl.enums import GLDrawMode, GLIndexType
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.gpu.buffers.helper import as_vec3_array
from picogl.gpu.buffers.vertex.vbo.vbo_class import MeshDataAttrs, VBOType
from picogl.shaders.type import ShaderType

if TYPE_CHECKING:
    from picogl.renderer.meshdata import MeshData


def expand_triangle_vertices_and_colors(
    a: int,
    b: int,
    c: int,
    colors: ndarray,
    expanded_colors: ndarray,
    expanded_vertices: ndarray,
    triangle_index: int,
    vertices: ndarray,
) -> None:
    """
    expand_triangle_vertices_and_colors
    """
    expanded_vertices[3 * triangle_index + 0] = vertices[a]
    expanded_vertices[3 * triangle_index + 1] = vertices[b]
    expanded_vertices[3 * triangle_index + 2] = vertices[c]

    expanded_colors[3 * triangle_index + 0] = colors[a]
    expanded_colors[3 * triangle_index + 1] = colors[b]
    expanded_colors[3 * triangle_index + 2] = colors[c]


def empty_triangle_vertices(triangle_count: int, components: int = 3) -> ndarray:
    """
    empty_triangle_vertices
    """
    return np.empty((triangle_count * 3, components), dtype=np.float32)


class GLMesh:
    """
    GPU-resident geometry: owns VAO/VBO and optional EBO/CBO/NBO buffers.
    It does not know anything about shaders or matrices.
    """

    def __init__(
        self,
        vertices: np.ndarray,
        faces: Optional[np.ndarray] = None,
        colors: Optional[np.ndarray] = None,
        normals: Optional[np.ndarray] = None,
        uvs: Optional[np.ndarray] = None,
        use_indices: bool = True,
        *,
        shader_type: Literal[
            ShaderType.ISOSURFACE,
            ShaderType.RIBBONS,
            ShaderType.TEXTURES,
        ] = ShaderType.ISOSURFACE,
        registry_label: Optional[str] = None,
    ):
        self.vao: Optional[VertexArrayObject] = None
        self.index_count: int = 0
        self.mesh: Optional["MeshData"] = None
        # strict (N, 3)
        self.vertices = as_vec3_array(vertices)

        # Missing/empty faces select direct glDrawArrays rendering.
        self.indices = (
            np.asarray(faces, dtype=np.uint32).reshape(-1)
            if faces is not None
            else np.array([], dtype=np.uint32)
        )
        nverts = self.vertices.shape[0]

        if self.indices.size > 0 and self.indices.size % 3 != 0:
            raise ValueError(
                "GLMesh: faces must define a multiple of 3 indices (triangles)"
            )

        self.use_indices = bool(use_indices and self.indices.size > 0)
        if shader_type not in (
            ShaderType.ISOSURFACE,
            ShaderType.RIBBONS,
            ShaderType.TEXTURES,
        ):
            raise ValueError(
                "shader_type must be ShaderType.ISOSURFACE, "
                "ShaderType.RIBBONS, or ShaderType.TEXTURES"
            )
        self.shader_type = shader_type
        self._registry_label = registry_label

        self.colors = (
            as_vec3_array(colors)
            if colors is not None
            else np.tile((0.0, 0.0, 1.0), (nverts, 1)).astype(np.float32)
        )
        self.normals = (
            as_vec3_array(normals)
            if normals is not None
            else np.zeros_like(self.vertices)
        )
        self.uvs = (
            np.asarray(uvs, dtype=np.float32).reshape(-1, 2)
            if uvs is not None
            else np.zeros((nverts, 2), dtype=np.float32)
        )

        # If non-indexed path is requested, prepare expanded data (optional)
        self._expanded_vertices = None  # per-triangle vertices if needed
        self._expanded_colors = None
        self._expanded_normals = None
        self._expanded_uvs = None
        self._layouts = build_shader_layouts()
        self._layout_descriptor = self._layouts[shader_type]
        if not self.use_indices and self.indices.size > 0:
            self._expand_to_non_indexed()

    def _get_buffer_data(self, vbo_type: VBOType) -> Optional[np.ndarray]:
        """get_buffer_data(vbo_type) -> np.ndarray"""
        return {
            VBOType.VBO: self.vertices,
            VBOType.CBO: self.colors,
            VBOType.NBO: self.normals,
            VBOType.UVS: self.uvs,
        }.get(vbo_type)

    def _expand_to_non_indexed(self) -> None:
        """
        Expand the mesh so that every triangle has its own copy of vertices/colors/normals/uvs.
        This converts indexed data (shared vertices) into a per-triangle vertex list suitable
        for glDrawArrays. The API remains the same; just keep the EBO empty and set index_count accordingly.
        """
        if self.indices is None or self.indices.size == 0:
            raise ValueError("Cannot expand: no indices to expand from")

        # For each triangle, fetch its three vertices and associated attributes
        v = self.vertices
        c = self.colors
        n = self.normals
        t = self.uvs

        # Build per-triangle vertex lists
        tri_count = self.indices.size // 3
        expanded_v = empty_triangle_vertices(tri_count)
        expanded_c = empty_triangle_vertices(tri_count)
        expanded_n = empty_triangle_vertices(tri_count)
        expanded_t = empty_triangle_vertices(
            tri_count, components=2
        )  # np.empty((tri_count * 3, 2), dtype=np.float32)

        for i in range(tri_count):
            a = self.indices[3 * i + 0]
            b = self.indices[3 * i + 1]
            cidx = self.indices[3 * i + 2]

            expand_vertices_colors(a, b, c, cidx, expanded_c, expanded_v, i, v)

            expand_vertices_colors(a, b, t, cidx, expanded_t, expanded_n, i, n)

        self._expanded_vertices = expanded_v
        self._expanded_colors = expanded_c
        self._expanded_normals = expanded_n
        self._expanded_uvs = expanded_t

        # After expansion, there are no indices to upload
        self.vertices = expanded_v
        self.colors = expanded_c
        self.normals = expanded_n
        self.uvs = expanded_t
        self.indices = np.array([], dtype=np.uint32)
        self.index_count = expanded_v.shape[0]  # equals tri_count * 3

    @classmethod
    def from_mesh_data(
        cls,
        mesh: "MeshData",
        *,
        vertex_layout: Union[
            ShaderType.ISOSURFACE,
            ShaderType.RIBBONS,
            ShaderType.TEXTURES,
        ] = ShaderType.ISOSURFACE,
        registry_label: Optional[str] = None,
    ) -> "GLMesh":
        """
        Construct a GLMesh from a MeshData container.

        Parameters
        ----------
        mesh : MeshData
            Must have vertices (Nx3). Indices are optional; geometry without
            indices is rendered directly with ``glDrawArrays``.
        vertex_layout :
            ``surface`` → attr order pos, color, normal (``surface_with_lighting`` / mesh).
            ``ribbon`` → pos, normal, color (``ribbons``).

        Returns
        -------
        GLMesh
            Ready-to-upload mesh (GPU buffers are allocated only when `upload()` is called).
        """
        gl_mesh = cls(
            vertices=mesh.vertices,
            faces=mesh.indices,
            colors=mesh.colors,
            normals=mesh.normals,
            uvs=getattr(mesh, MeshDataAttrs.TEXCOORDS, None),
            shader_type=vertex_layout,
            registry_label=registry_label,
        )
        gl_mesh.mesh = mesh
        return gl_mesh

    def _color_attrib_index(self) -> int:
        """Vertex attribute index for the color buffer in this mesh layout."""
        from picogl.gpu.buffers.vertex.vbo.vbo_class import VBOType

        for attr in self._layout_descriptor.attributes:
            if attr.vbo_type == VBOType.CBO:
                return int(attr.index)
        return 1

    def update_colors(self, colors: np.ndarray):
        self.colors = colors.astype(np.float32)

        if not self.vao:
            return

        color_index = self._color_attrib_index()
        has_color_vbo = False
        modern_vbo_for = getattr(self.vao, "_modern_vbo_for_attrib", None)
        if callable(modern_vbo_for):
            has_color_vbo = modern_vbo_for(color_index) is not None

        if not has_color_vbo:
            # VAO was uploaded before colors existed (MeshData defaults colours to
            # zero); drop GPU state so the next upload() includes the colour VBO.
            self.delete()
            return

        self.vao.update_vbo(index=color_index, data=self.colors)

    def upload(self) -> None:
        """Allocate & fill GPU buffers."""

        if self.vao:
            is_valid = getattr(self.vao, "is_valid_in_current_context", None)
            if callable(is_valid) and not is_valid():
                self.delete()
            else:
                return  # already uploaded
        vao: Optional[VertexArrayObject] = None
        try:
            vao = VertexArrayObject(registry_label=self._registry_label)
            descriptor = self._layout_descriptor
            for attr in descriptor.attributes:
                data = self._get_buffer_data(attr.vbo_type)
                if data is None or getattr(data, "size", 0) == 0:
                    continue

                vao.add_vbo(
                    name=attr.name,
                    data=data,
                    index=attr.index,
                    size=attr.size,
                )

            # Legacy fallback: older layouts omitted UV from the descriptor.
            if self.uvs is not None and not any(
                attr.vbo_type == VBOType.UVS for attr in descriptor.attributes
            ):
                vao.add_vbo(data=self.uvs, index=3, size=2)

            if self.use_indices:
                vao.add_ebo(data=self.indices)

            # vao.configure_from_descriptor(descriptor)
            self.vao = vao
            if self.mesh is not None:
                self.mesh.attach_vao(vao)
            self.index_count = (
                self.indices.size if self.use_indices else self.vertices.shape[0]
            )
            vao = None  # ownership transferred to self.vao
        finally:
            # If add_vbo/add_ebo failed after VAO gen, drop orphan VAO so the next
            # upload() retry does not accumulate registry leaks.
            if vao is not None:
                gl_release_vertex_array_object(vao)

    def bind(self):
        self.upload()
        if not self.vao:
            raise RuntimeError("GLMesh not uploaded")
        self.vao.__enter__()  # context protocol

    def unbind(self):
        if self.vao:
            self.vao.__exit__(None, None, None)

    def delete(self):
        """Free GPU resources."""
        if self.vao:
            gl_release_vertex_array_object(self.vao)
            self.vao = None
            self.index_count = 0

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.unbind()

    def draw(self, mode: GLDrawMode = GLDrawMode.TRIANGLES) -> None:
        """Draw via attached :class:`MeshData` when its CPU arrays are intact.

        ElMo secondary-structure drawables copy arrays into this object then
        call :meth:`MeshData.delete`. ``MeshData.draw`` needs those arrays for
        :meth:`~picogl.renderer.meshdata.MeshData.draw_spec`; once they are
        gone, issue ``glDraw*`` from the uploaded VAO and ``index_count``.
        """
        if not self.vao:
            raise RuntimeError("GLMesh not uploaded. Call upload() first.")
        mesh = self.mesh
        if (
            mesh is not None
            and getattr(mesh, "vao", None) is not None
            and getattr(mesh, "vertices", None) is not None
        ):
            mesh.draw()
            return
        with self.vao:
            self.vao.draw(
                index_count=self.index_count,
                mode=mode,
                dtype=GLIndexType.UNSIGNED_INT,
                pointer=ctypes.c_void_p(0),
            )
