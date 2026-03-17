import ctypes
from typing import Optional

import numpy as np
from picogl.buffers.factory.layout import create_layout
from OpenGL.GL import glDrawElements
from OpenGL.raw.GL._types import GL_FLOAT
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_COLOR_ARRAY, GL_VERTEX_ARRAY, glDrawArrays

from picogl.backend.legacy.core.vertex.buffer.client_states import legacy_client_states
from picogl.buffers.attributes import AttributeSpec
from picogl.buffers.glcleanup import delete_buffer_object
from picogl.buffers.vertex.legacy import VertexBufferGroup


class LegacyGLMeshNew:
    """
    GL Mesh for Compatibility Profile (Legacy OpenGL)

    Keeps a similar interface to theIndexed version, but uses
    client-side arrays / legacy calls instead of VAOs/VBOs/EBOs.
    """

    def __init__(
        self,
        vertices: np.ndarray,
        faces: Optional[np.ndarray],
        colors: Optional[np.ndarray] = None,
        normals: Optional[np.ndarray] = None,
        uvs: Optional[np.ndarray] = None,
        use_indices: bool = True,
    ):
        # strict (N, 3)
        self.vertices = np.asarray(vertices, dtype=np.float32).reshape(-1, 3)

        if faces is not None:
            self.indices = np.asarray(faces, dtype=np.uint32).reshape(-1)
        else:
            self.indices = np.array([], dtype=np.uint32)

        nverts = self.vertices.shape[0]

        # Validation: must have non-empty faces when using indexed path
        if self.indices.size == 0:
            raise ValueError("LegacyGLMesh requires non-empty faces")

        # If indices are used, ensure they form complete triangles
        if self.indices.size % 3 != 0:
            raise ValueError("LegacyGLMesh: faces must define a multiple of 3 indices (triangles)")

        self.use_indices = use_indices  # allow an easy switch to non-indexed path

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

        self.vao = None  # keep name for compatibility
        self.index_count: int = self.indices.size

        # Optional expanded data for non-indexed path
        self._expanded_vertices = None
        self._expanded_colors = None
        self._expanded_normals = None
        self._expanded_uvs = None

        if not self.use_indices:
            self._expand_to_non_indexed()

    @classmethod
    def from_mesh_data(cls, mesh: "MeshDataLegacy") -> "LegacyGLMesh":
        return cls(
            vertices=mesh.vbo,
            faces=mesh.ebo,
            colors=mesh.cbo,
            normals=mesh.nbo,
            uvs=getattr(mesh, "uvs", None),
        )

    def _expand_to_non_indexed(self) -> None:
        """
        Expand indexed data to per-triangle vertex data for glDrawArrays.
        """
        if self.indices is None or self.indices.size == 0:
            raise ValueError("Cannot expand: no indices to expand from")

        v = self.vertices
        c = self.colors
        n = self.normals
        t = self.uvs

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

        self.vertices = expanded_v
        self.colors = expanded_c
        self.normals = expanded_n
        self.uvs = expanded_t
        self.indices = np.array([], dtype=np.uint32)
        self.index_count = expanded_v.shape[0]

    def upload(self) -> None:
        """Legacy GL uses client-side arrays; minimal setup is preserved for compatibility."""
        # In legacy GL, upload typically isn't necessary for client arrays,
        # but we keep a placeholder to maintain API compatibility.
        if self.vao:
            return
        # If you want to precompute a single contiguous block, you could store lists here.
        self.vao = None  # no VAO in legacy immediate mode

        # index_count already set during __init__ or _expand_to_non_indexed
        # For clarity, ensure it's correct:
        self.index_count = self.indices.size if self.use_indices else self.vertices.shape[0]

    def bind(self):
        # Legacy GL uses client arrays; no VAO binding. We might enable client states here.
        pass

    def unbind(self):
        pass

    def delete(self):
        """Legacy GL doesn’t hold GPU resources in VAOs/VBOs; keep API for symmetry."""
        self.vao = None
        self.index_count = 0

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.unbind()

    def draw(self, mode=GL_TRIANGLES) -> None:
        """Draw the mesh using Legacy GL calls."""
        try:
            # In legacy GL, ensure data pointers are set before drawing.
            if self.use_indices and self.index_count > 0:
                # If you are using client-side element arrays, you can call:
                # glDrawElements(mode, index_count, GL_UNSIGNED_INT, self.indices.ctypes.data)
                # But most modern Python OpenGL wrappers expect numpy buffers; adapt as needed.
                glDrawElements(mode, int(self.index_count), GL_UNSIGNED_INT, ctypes.c_void_p(0))
            else:
                # Non-indexed path: draw as arrays. We'll draw as triangles from vertex data.
                glDrawArrays(mode, 0, int(self.index_count))
        except Exception as ex:
            raise


class LegacyGLMesh:
    """
    GL Mesh fir Compatibility Profile

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
        if faces is not None:
            self.indices = np.asarray(faces, dtype=np.uint32).reshape(-1)
        else:
            self.indices = np.array([], dtype=np.uint32)
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

        self.vao: Optional[VertexBufferGroup] = None
        self.index_count: int = 0

    @classmethod
    def from_mesh_data(cls, mesh: "MeshDataLegacy") -> "LegacyGLMesh":
        """
        Construct a GLMesh from a MeshDataLegacy container.

        Parameters
        ----------
        mesh : MeshDataLegacy
            Must have .vbo (Nx3), .ebo (Mx1), optional .cbo (Nx3), .nbo (Nx3), uvs (Nx2)

        Returns
        -------
        LegacyGLMesh
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

        attributes = self.generate_dynamic_attributes()
        vao_layout = create_layout(attributes)

        self.vao = vao = VertexBufferGroup()
        vao.add_vbo(data=self.vertices, name="vbo", size=3)
        vao.add_vbo(data=self.colors, name="cbo", size=3)
        vao.add_vbo(data=self.normals, name="nbo", size=3)
        if self.uvs is not None:
            vao.add_vbo(data=self.uvs, name="uvs", size=2)
        vao.add_ebo(data=self.indices)
        vao.set_layout(vao_layout)

        self.index_count = self.indices.size

    def generate_dynamic_attributes(self):
        """
        generate_dynamic_attributes

        Create layout that matches the VBOs being added
        """
        attributes = [
            AttributeSpec(
                name="positions",
                index=0,
                size=3,
                type=GL_FLOAT,
                normalized=False,
                stride=0,
                offset=0,
            ),
            AttributeSpec(
                name="colors",
                index=1,
                size=3,
                type=GL_FLOAT,
                normalized=False,
                stride=0,
                offset=0,
            ),
            AttributeSpec(
                name="normals",
                index=2,
                size=3,
                type=GL_FLOAT,
                normalized=False,
                stride=0,
                offset=0,
            ),
        ]
        # Add UVs attribute if UVs are provided
        if self.uvs is not None:
            attributes.append(
                AttributeSpec(
                    name="uvs",
                    index=3,
                    size=2,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                )
            )
        return attributes

    def bind(self):
        if not self.vao:
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

    def draw(self, mode=GL_TRIANGLES) -> None:
        """Draw the mesh."""
        try:
            if not self.vao:
                raise RuntimeError("GLMesh not uploaded. Call upload() first.")

            # Use legacy client states and individual VBOs to bypass the problematic bind() method
            with legacy_client_states(GL_VERTEX_ARRAY, GL_COLOR_ARRAY):
                with self.vao.vbo, self.vao.cbo, self.vao.ebo:
                    glDrawElements(
                        mode, int(self.index_count), GL_UNSIGNED_INT, ctypes.c_void_p(0)
                    )
        except Exception as ex:
            print(f"Error drawing mesh: {ex}")
