import ctypes
from typing import Optional

import numpy as np
from OpenGL.GL import glDrawElements
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.buffers.glcleanup import delete_buffer_object


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
    ):
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

        self.vao: Optional[VertexArrayObject] = None
        self.index_count: int = 0

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
    def from_mesh_data(cls, mesh: "MeshData") -> "GLMesh":
        """
        Construct a GLMesh from a MeshData container.

        Parameters
        ----------
        mesh : MeshData
            Must have .vbo (Nx3), .ebo (Mx1), optional .cbo (Nx3), .nbo (Nx3), uvs (Nx2)

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
            uvs=getattr(mesh, "uvs", None),
        )

    def upload(self) -> None:
        """Allocate & fill GPU buffers."""
        if self.vao:
            return  # already uploaded

        vao = VertexArrayObject()
        vao.add_vbo(data=self.vertices, index=0, size=3)
        vao.add_vbo(data=self.colors, index=1, size=3)
        vao.add_vbo(data=self.normals, index=2, size=3)
        if self.uvs is not None:
            vao.add_vbo(data=self.uvs, index=3, size=2)

        if self.use_indices:
            vao.add_ebo(data=self.indices)

        self.vao = vao
        self.index_count = self.indices.size if self.use_indices else self.vertices.shape[0]

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
