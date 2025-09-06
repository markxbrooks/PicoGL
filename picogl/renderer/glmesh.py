import ctypes
from typing import Optional

import numpy as np
from OpenGL.GL import glDrawElements
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES, GL_UNSIGNED_INT

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
    ):
        # strict (N, 3)
        self.vertices = np.asarray(vertices, dtype=np.float32).reshape(-1, 3)
        self.indices = np.asarray(faces, dtype=np.uint32).reshape(-1)
        nverts = self.vertices.shape[0]

        if self.indices.size == 0:
            raise ValueError("GLMesh requires non-empty faces")

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
        vao.add_ebo(data=self.indices)

        self.vao = vao
        self.index_count = self.indices.size

    def bind(self):
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
                glDrawElements(
                    GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, ctypes.c_void_p(0)
                )
        except Exception as ex:
            print(ex)
