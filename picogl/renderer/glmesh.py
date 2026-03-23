import ctypes
from typing import TYPE_CHECKING, Literal, Optional

import numpy as np
from OpenGL.GL import glDrawElements
from OpenGL.raw.GL._types import GL_FLOAT
from OpenGL.raw.GL.ARB.vertex_array_object import glBindVertexArray
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.backend.modern.core.vertex.buffer.element import ModernEBO
from picogl.backend.modern.core.vertex.buffer.object import ModernVBO
from picogl.buffers.attributes import AttributeSpec, LayoutDescriptor
from picogl.buffers.glcleanup import delete_buffer_object
from picogl.buffers.vertex.vbo.vbo_class import VBOType

if TYPE_CHECKING:
    from picogl.renderer.meshdata import MeshData


def get_layout_for(vertex_layout: Literal["surface", "ribbon"]) -> LayoutDescriptor:
    """
    Build a :class:`LayoutDescriptor` for :class:`GLMeshModern` interleaved storage.

    CPU / interleaved order is always ``position, normal, color, uv`` (see
    :meth:`GLMeshModern._build_interleaved`). Shader attribute locations differ:

    - ``surface``: locations ``0=pos, 1=color, 2=normal, 3=uv`` (surface / bonds mesh shaders).
    - ``ribbon``: ``0=pos, 1=normal, 2=color, 3=uv`` (ribbons shader).
    """
    if vertex_layout not in ("surface", "ribbon"):
        raise ValueError(f"vertex_layout must be 'surface' or 'ribbon', got {vertex_layout!r}")
    # Interleaved: vec3 pos, vec3 normal, vec3 color, vec2 uv → 11 floats → 44 bytes
    stride = 44
    if vertex_layout == "ribbon":
        return LayoutDescriptor(
            attributes=[
                AttributeSpec("position", 0, 3, GL_FLOAT, False, stride, 0),
                AttributeSpec("normal", 1, 3, GL_FLOAT, False, stride, 12),
                AttributeSpec("color", 2, 3, GL_FLOAT, False, stride, 24),
                AttributeSpec("uv", 3, 2, GL_FLOAT, False, stride, 36),
            ]
        )
    return LayoutDescriptor(
        attributes=[
            AttributeSpec("position", 0, 3, GL_FLOAT, False, stride, 0),
            AttributeSpec("color", 1, 3, GL_FLOAT, False, stride, 24),
            AttributeSpec("normal", 2, 3, GL_FLOAT, False, stride, 12),
            AttributeSpec("uv", 3, 2, GL_FLOAT, False, stride, 36),
        ]
    )


class GLMeshModern:
    """
    Modern GLMesh using:
    - Interleaved VBO
    - Your existing VertexArrayObject + LayoutDescriptor
    """

    def __init__(
        self,
        vertices: np.ndarray,
        indices: Optional[np.ndarray] = None,
        normals: Optional[np.ndarray] = None,
        colors: Optional[np.ndarray] = None,
        uvs: Optional[np.ndarray] = None,
        layout: Optional["LayoutDescriptor"] = None,
    ):
        self.vertices = np.asarray(vertices, dtype=np.float32).reshape(-1, 3)
        n = self.vertices.shape[0]

        self.normals = (
            np.asarray(normals, dtype=np.float32).reshape(-1, 3)
            if normals is not None
            else np.zeros((n, 3), dtype=np.float32)
        )

        self.colors = (
            np.asarray(colors, dtype=np.float32).reshape(-1, 3)
            if colors is not None
            else np.ones((n, 3), dtype=np.float32)
        )

        self.uvs = (
            np.asarray(uvs, dtype=np.float32).reshape(-1, 2)
            if uvs is not None
            else np.zeros((n, 2), dtype=np.float32)
        )

        self.indices = (
            np.asarray(indices, dtype=np.uint32).reshape(-1)
            if indices is not None
            else None
        )

        self.vertex_count = n
        self.index_count = 0 if self.indices is None else self.indices.size

        # GPU
        self.vao: Optional[VertexArrayObject] = None
        self.vbo: Optional[ModernVBO] = None
        self.ebo: Optional[ModernEBO] = None

        self.layout = layout
        self._uploaded = False

    # ------------------------------------------------------------------
    # Interleaved buffer
    # ------------------------------------------------------------------
    def _build_interleaved(self) -> np.ndarray:
        return np.hstack([
            self.vertices,
            self.normals,
            self.colors,
            self.uvs,
        ]).astype(np.float32)

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------
    def upload(self):
        if self._uploaded:
            return

        interleaved = self._build_interleaved()

        stride = interleaved.shape[1] * 4  # float32 = 4 bytes

        self.vao = VertexArrayObject()
        self.vao.bind()

        # --- VBO ---
        self.vbo = ModernVBO()
        self.vbo.bind()
        self.vbo.set_data(interleaved)

        # --- Layout (CRITICAL) ---
        if self.layout is None:
            raise RuntimeError("LayoutDescriptor required for GLMeshModern")

        # Patch layout stride dynamically
        for attr in self.layout.attributes:
            attr.stride = stride

        self.vao.vbo = self.vbo
        self.vao.layout = self.layout
        # VertexArrayObject.set_layout early-outs if ``self.vao`` is None (legacy gate; misnamed).
        self.vao.vao = self.vao.handle
        self.vao.configure()

        # --- EBO ---
        if self.indices is not None:
            self.ebo = ModernEBO(data=self.indices)
            self.ebo.bind()
            self.vao.ebo = self.ebo

        glBindVertexArray(0)

        self._uploaded = True

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def draw(self):
        if not self._uploaded:
            self.upload()

        if not self.vao:
            raise RuntimeError("VAO not initialized")

        with self.vao.bound():
            if self.indices is not None:
                glDrawElements(
                    GL_TRIANGLES,
                    self.index_count,
                    GL_UNSIGNED_INT,
                    ctypes.c_void_p(0),
                )
            else:
                glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def delete(self):
        if self.vao:
            self.vao.delete_buffers()
            self.vao.delete()
            self.vao = None

        self.vbo = None
        self.ebo = None
        self._uploaded = False

    @classmethod
    def from_mesh_data(
            cls,
            mesh: "MeshData",
            *,
            vertex_layout: Literal["surface", "ribbon"] = "surface",
    ) -> "GLMeshModern":
        """
        Construct a GLMesh from a MeshData container.

        Parameters
        ----------
        mesh : MeshData
            Must have .vbo (Nx3), .ebo (Mx1), optional .cbo (Nx3), .nbo (Nx3), uvs (Nx2)
        vertex_layout :
            ``surface`` → attr order pos, color, normal (``surface_with_lighting`` / mesh).
            ``ribbon`` → pos, normal, color (``ribbons`` / RibbonVAO).

        Returns
        -------
        GLMesh
            Ready-to-upload mesh (GPU buffers are allocated only when `upload()` is called).
        """
        return cls(
            vertices=mesh.vbo,
            indices=mesh.ebo,
            colors=mesh.cbo,
            normals=mesh.nbo,
            uvs=getattr(mesh, VBOType.UVS, None),
            layout=get_layout_for(vertex_layout),
        )

    def update_colors(self, colors: np.ndarray):
        self.colors = colors.astype(np.float32)

        if self.vao:
            self.vao.update_vbo(index=1, data=self.colors)  # CBO slot

class GLMesh:
    """
    GPU‐resident mesh: owns VAO/VBO/EBO/CBO/NBO for an indexed triangle mesh.
    It does not know anything about shaders or matrices.
    """

    def __init__(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        colors: Optional[np.ndarray] = None,
        normals: Optional[np.ndarray] = None,
        uvs: Optional[np.ndarray] = None,
        use_indices: bool = True,
        *,
        vertex_layout: Literal["surface", "ribbon"] = "surface",
    ):
        self.vao: Optional[VertexArrayObject] = None
        self.index_count: int = 0
        # strict (N, 3)
        self.vertices = np.asarray(vertices, dtype=np.float32).reshape(-1, 3)

        # If using indices, expect a flat array of indices
        self.indices = np.asarray(faces, dtype=np.uint32).reshape(-1)
        nverts = self.vertices.shape[0]

        if self.indices.size == 0:
            raise ValueError("GLMesh requires non-empty faces")

        # Validate that we have a multiple of 3 indices for triangles
        if self.indices.size % 3 != 0:
            raise ValueError("GLMesh: faces must define a multiple of 3 indices (triangles)")

        self.use_indices = use_indices  # present for compatibility and potential path changes
        if vertex_layout not in ("surface", "ribbon"):
            raise ValueError("vertex_layout must be 'surface' or 'ribbon'")
        self.vertex_layout = vertex_layout

        self.colors = (
            np.asarray(colors, dtype=np.float32).reshape(-1, 3)
            if colors is not None
            else np.tile((0.0, 0.0, 1.0), (nverts, 1)).astype(np.float32)
        )
        self.normals = (
            np.asarray(normals, dtype=np.float32).reshape(-1, 3)
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

        if not self.use_indices:
            self._expand_to_non_indexed()

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
        expanded_v = np.empty((tri_count * 3, 3), dtype=np.float32)
        expanded_c = np.empty((tri_count * 3, 3), dtype=np.float32)
        expanded_n = np.empty((tri_count * 3, 3), dtype=np.float32)
        expanded_t = np.empty((tri_count * 3, 2), dtype=np.float32)

        for i in range(tri_count):
            a = self.indices[3 * i + 0]
            b = self.indices[3 * i + 1]
            cidx = self.indices[3 * i + 2]

            expanded_v[3 * i + 0] = v[a]
            expanded_v[3 * i + 1] = v[b]
            expanded_v[3 * i + 2] = v[cidx]

            expanded_c[3 * i + 0] = c[a]
            expanded_c[3 * i + 1] = c[b]
            expanded_c[3 * i + 2] = c[cidx]

            expanded_n[3 * i + 0] = n[a]
            expanded_n[3 * i + 1] = n[b]
            expanded_n[3 * i + 2] = n[cidx]

            expanded_t[3 * i + 0] = t[a]
            expanded_t[3 * i + 1] = t[b]
            expanded_t[3 * i + 2] = t[cidx]

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
        vertex_layout: Literal["surface", "ribbon"] = "surface",
    ) -> "GLMesh":
        """
        Construct a GLMesh from a MeshData container.

        Parameters
        ----------
        mesh : MeshData
            Must have .vbo (Nx3), .ebo (Mx1), optional .cbo (Nx3), .nbo (Nx3), uvs (Nx2)
        vertex_layout :
            ``surface`` → attr order pos, color, normal (``surface_with_lighting`` / mesh).
            ``ribbon`` → pos, normal, color (``ribbons`` / RibbonVAO).

        Returns
        -------
        GLMesh
            Ready-to-upload mesh (GPU buffers are allocated only when `upload()` is called).
        """
        return cls(
            vertices=mesh.vbo,
            faces=mesh.ebo,
            colors=mesh.cbo,
            normals=mesh.nbo,
            uvs=getattr(mesh, VBOType.UVS, None),
            vertex_layout=vertex_layout,
        )

    def update_colors(self, colors: np.ndarray):
        self.colors = colors.astype(np.float32)

        if self.vao:
            self.vao.update_vbo(index=1, data=self.colors)  # CBO slot

    def upload(self) -> None:
        """Allocate & fill GPU buffers."""
        if self.vao:
            return  # already uploaded

        vao: Optional[VertexArrayObject] = None
        try:
            vao = VertexArrayObject()
            if self.vertex_layout == "ribbon":
                # Match elmo/glsl/src/ribbons/vertex.glsl (and RibbonVAO)
                vao.add_vbo(data=self.vertices, index=0, size=3)
                vao.add_vbo(data=self.normals, index=1, size=3)
                vao.add_vbo(data=self.colors, index=2, size=3)
            else:
                # Match elmo/glsl/src/surface_with_lighting/vertex.glsl
                vao.add_vbo(data=self.vertices, index=0, size=3)
                vao.add_vbo(data=self.colors, index=1, size=3)
                vao.add_vbo(data=self.normals, index=2, size=3)
            if self.uvs is not None:
                vao.add_vbo(data=self.uvs, index=3, size=2)

            if self.use_indices:
                vao.add_ebo(data=self.indices)

            self.vao = vao
            self.index_count = (
                self.indices.size if self.use_indices else self.vertices.shape[0]
            )
            vao = None  # ownership transferred to self.vao
        finally:
            # If add_vbo/add_ebo failed after VAO gen, drop orphan VAO so the next
            # upload() retry does not accumulate registry leaks.
            if vao is not None:
                delete_buffer_object(vao)

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
            delete_buffer_object(self.vao)
            self.vao = None
            self.index_count = 0

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.unbind()

    def draw(self) -> None:
        """Draw the mesh."""
        try:
            if not self.vao:
                raise RuntimeError("GLMesh not uploaded. Call upload() first.")
            with self.vao:
                if self.use_indices and self.index_count > 0:
                    glDrawElements(
                        GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, ctypes.c_void_p(0)
                    )
                else:
                    glDrawArrays(GL_TRIANGLES, 0, self.index_count)
        except Exception as e:
            # You might want to log e or re-raise
            raise


