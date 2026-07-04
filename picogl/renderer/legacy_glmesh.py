"""
Module for creating and managing GPU-resident meshes in a legacy OpenGL
compatibility profile.

This module defines the LegacyGLMesh class, which represents an indexed
triangle mesh. It provides functionality for uploading mesh data to GPU
buffers, managing their lifecycle, and rendering the mesh.

Classes
-------
LegacyGLMesh
    Represents a GPU-resident mesh with VAO/VBO/EBO/CBO/NBO structures
    for an indexed triangle mesh.
"""

from typing import Optional

import numpy as np
from picogl.backend.gl.enums import GLDrawMode, GLNumeric
from picogl.backend.gl.state.client import GLClientState
from picogl.backend.gl.wrappers import gl_draw_elements
from picogl.backend.gl.wrappers.glcleanup import gl_delete_buffer_object
from picogl.backend.legacy.core.vertex.buffer.client_states import \
    legacy_client_states
from picogl.gpu.buffers.attributes import (AttributeSpec, CanonicalVertexAttrs,
                                           legacy_attribute_spec)
from picogl.gpu.buffers.factory import create_layout
from picogl.gpu.buffers.helper import as_vec3_array
from picogl.gpu.buffers.vertex.aliases import VertexBufferRole
from picogl.gpu.buffers.vertex.legacy import VertexBufferGroup
from picogl.gpu.buffers.vertex.vbo.vbo_class import MeshDataAttrs, VBOType


class LegacyGLMesh:
    """
    gl Mesh fir Compatibility Profile

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
        self.vertices = as_vec3_array(vertices)
        if faces is not None:
            self.indices = np.asarray(faces, dtype=np.uint32).reshape(-1)
        else:
            self.indices = np.array([], dtype=np.uint32)
        nverts = self.vertices.shape[0]

        if self.indices.size == 0:
            raise ValueError("GLMesh requires non-empty faces")

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

        self.vao: Optional[VertexBufferGroup] = None
        self.index_count: int = 0

    @classmethod
    def from_mesh_data(cls, mesh: "MeshData") -> "LegacyGLMesh":
        """
        Construct a GLMesh from a MeshData container.

        Parameters
        ----------
        mesh : MeshData
            Must have .vertices (Nx3), .ebo (Mx1), optional .cbo (Nx3), .nbo (Nx3), uvs (Nx2)

        Returns
        -------
        LegacyGLMesh
            Ready-to-upload mesh (GPU buffers are allocated only when `upload()` is called).
        """
        return cls(
            vertices=mesh.vertices,
            faces=mesh.indices,
            colors=mesh.colors,
            normals=mesh.normals,
            uvs=getattr(mesh, MeshDataAttrs.TEXCOORDS, None),
        )

    def upload(self) -> None:
        """Allocate & fill GPU buffers."""
        if self.vao:
            return  # already uploaded

        attributes = self.generate_dynamic_attributes()
        vao_layout = create_layout(attributes)

        self.vao = vao = VertexBufferGroup()
        vao.add_vbo(data=self.vertices, name=VBOType.VBO, size=3)
        vao.add_vbo(data=self.colors, name=VBOType.CBO, size=3)
        vao.add_vbo(data=self.normals, name=VBOType.NBO, size=3)
        if self.uvs is not None:
            vao.add_vbo(data=self.uvs, name=VBOType.UVS, size=2)
        vao.add_ebo(data=self.indices)
        vao.set_layout(vao_layout)

        self.index_count = self.indices.size

    def generate_dynamic_attributes(self):
        """
        generate_dynamic_attributes

        Create layout that matches the VBOs being added
        """
        attributes = [
            legacy_attribute_spec(
                VertexBufferRole.VBO,
                0,
                name=CanonicalVertexAttrs.POSITIONS,
                type=GLNumeric.FLOAT,
            ),
            legacy_attribute_spec(
                VertexBufferRole.CBO,
                1,
                name=CanonicalVertexAttrs.COLORS,
                type=GLNumeric.FLOAT,
            ),
            legacy_attribute_spec(
                VertexBufferRole.NBO,
                2,
                name=CanonicalVertexAttrs.NORMALS,
                type=GLNumeric.FLOAT,
            ),
        ]
        # Add UVs attribute if UVs are provided
        if self.uvs is not None:
            attributes.append(
                AttributeSpec(
                    name=VBOType.UVS,
                    index=3,
                    size=2,
                    type=GLNumeric.FLOAT,
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
            gl_delete_buffer_object(self.vao)
            self.vao = None
            self.index_count = 0

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.unbind()

    def draw(self, mode=GLDrawMode.TRIANGLES) -> None:
        """Draw the mesh."""
        try:
            if not self.vao:
                raise RuntimeError("GLMesh not uploaded. Call upload() first.")

            # Use legacy client states and individual VBOs to bypass the problematic bind() method
            with legacy_client_states(GLClientState.VERTEX, GLClientState.COLOR):
                with self.vao.vbo, self.vao.cbo, self.vao.ebo:
                    gl_draw_elements(
                        int(self.index_count),
                        GLNumeric.UNSIGNED_INT,
                        mode,
                        pointer=None,
                        offset=0,
                    )
        except Exception as ex:
            print(f"Error drawing mesh: {ex}")
