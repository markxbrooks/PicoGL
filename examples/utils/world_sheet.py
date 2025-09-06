"""
World Sheet Widget
"""

import numpy as np
from OpenGL.GL import glGenBuffers, glGetUniformLocation, glUniformMatrix4fv
from OpenGL.GL.shaders import GL_FALSE
from OpenGL.raw.GL.ARB.vertex_shader import GL_FLOAT
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LINES
from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays
from OpenGL.raw.GL.VERSION.GL_1_5 import (
    GL_ARRAY_BUFFER,
    GL_STATIC_DRAW,
    glBindBuffer,
    glBufferData,
)
from OpenGL.raw.GL.VERSION.GL_2_0 import (
    glDisableVertexAttribArray,
    glEnableVertexAttribArray,
    glVertexAttribPointer,
)
from pyglm import glm

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.backend.modern.renderers.mesh import ShaderMeshRenderer


class WorldSheet(ShaderMeshRenderer):
    """World Sheer Viewer"""

    def __init__(self, base_dir: str, size: int = 10):
        """constructor"""
        super().__init__()
        self.line_buffer = None
        self.mvp_id = None
        self.base_dir = base_dir
        self.size = size

    def load_shader(self):
        """load shaders"""
        self.shader = ShaderProgram(
            "glsl/utils/worldsheet/vertex.glsl",
            "glsl/utils/worldsheet/fragment.glsl",
            glsl_dir=self.base_dir,
        )
        self.mvp_id = glGetUniformLocation(self.shader.program, "mvp_matrix")
        if self.mvp_id == -1:
            raise RuntimeError("MVP uniform not found in shader")

    def load_object(self):
        """load object"""
        lines = []
        for i in range(-self.size, self.size + 1):
            fi = float(i)
            lines.extend([-self.size, 0.0, fi, self.size, 0.0, fi])
            lines.extend([fi, 0.0, -self.size, fi, 0.0, self.size])
        self.lines = np.array(lines, dtype=np.float32)

        self.line_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.line_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.lines.nbytes, self.lines, GL_STATIC_DRAW)

    def load_texture(self):
        """load texture"""
        self.texture = None  # no texture for grid

    def render(self, mvp_matrix, view_matrix, projection_matrix):
        self.shader.begin()
        glUniformMatrix4fv(self.mvp_id, 1, GL_FALSE, glm.value_ptr(mvp_matrix))

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.line_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawArrays(GL_LINES, 0, len(self.lines) // 3)

        glDisableVertexAttribArray(0)
        self.shader.end()

    def run(self):
        raise NotImplementedError("Needs to be implemented")


if __name__ == "__main__":
    window = WorldSheet(base_dir=".")
    window.run()
