"""
GLContext class
"""

import numpy as np
from OpenGL import GL


class ModernMeshData:
    """Holds OpenGL-related state objects for modern rendering (VAO/VBO/EBO)."""

    def __init__(self, vertices, normals=None, uvs=None, colors=None, indices=None):
        self.vertex_count = len(vertices)

        # --- Create VAO ---
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        # --- VBO (positions) ---
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER, vertices.astype(np.float32), GL.GL_STATIC_DRAW
        )
        GL.glEnableVertexAttribArray(0)  # layout(location=0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 0, None)

        # --- NBO (normals) ---
        self.nbo = None
        if normals is not None:
            self.nbo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.nbo)
            GL.glBufferData(
                GL.GL_ARRAY_BUFFER, normals.astype(np.float32), GL.GL_STATIC_DRAW
            )
            GL.glEnableVertexAttribArray(1)  # layout(location=1)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 0, None)

        # --- CBO (colors) ---
        self.cbo = None
        if colors is not None:
            self.cbo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.cbo)
            GL.glBufferData(
                GL.GL_ARRAY_BUFFER, colors.astype(np.float32), GL.GL_STATIC_DRAW
            )
            GL.glEnableVertexAttribArray(2)  # layout(location=2)
            GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, False, 0, None)

        # --- UVs ---
        self.uvs = None
        if uvs is not None:
            self.uvs = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.uvs)
            GL.glBufferData(
                GL.GL_ARRAY_BUFFER, uvs.astype(np.float32), GL.GL_STATIC_DRAW
            )
            GL.glEnableVertexAttribArray(3)  # layout(location=3)
            GL.glVertexAttribPointer(3, 2, GL.GL_FLOAT, False, 0, None)

        # --- EBO (indices) ---
        self.ebo = None
        self.index_count = 0
        if indices is not None:
            self.ebo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            GL.glBufferData(
                GL.GL_ELEMENT_ARRAY_BUFFER, indices.astype(np.uint32), GL.GL_STATIC_DRAW
            )
            self.index_count = len(indices)

        # Unbind VAO
        GL.glBindVertexArray(0)

    def bind(self):
        GL.glBindVertexArray(self.vao)

    def unbind(self):
        GL.glBindVertexArray(0)

    def draw(self, mode=GL.GL_TRIANGLES):
        self.bind()
        if self.index_count > 0:
            GL.glDrawElements(mode, self.index_count, GL.GL_UNSIGNED_INT, None)
        else:
            GL.glDrawArrays(mode, 0, self.vertex_count)
        self.unbind()
