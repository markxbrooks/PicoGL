import glm
from meshViewer import meshWithRender
from OpenGL.GL import *  # pylint: disable=W0614

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.backend.modern.renderers.mesh import ShaderMeshRenderer
from .shaderLoader import Shader


from pyglm import glm
import numpy as np
from OpenGL.GL import *
from picogl.backend.modern.core.shader.program import ShaderProgram


class WorldSheet(ShaderMeshRenderer):
    def __init__(self, base_dir: str, size: int=10):
        super().__init__()
        self.mvp_id = None
        self.base_dir = base_dir
        self.size = size

    def load_shader(self):
        self.shader = ShaderProgram(
            "glsl/utils/worldsheet/vertex.glsl",
            "glsl/utils/worldsheet/fragment.glsl",
            glsl_dir=self.base_dir
        )
        self.mvp_id = glGetUniformLocation(self.shader.program, "mvp_matrix")
        if self.mvp_id == -1:
            raise RuntimeError("MVP uniform not found in shader")

    def load_object(self):
        lines = []
        for i in range(-self.size, self.size + 1):
            fi = float(i)
            lines.extend([-self.size, 0.0, fi, self.size, 0.0, fi])
            lines.extend([fi, 0.0, -self.size, fi, 0.0, self.size])
        self.lines = np.array(lines, dtype=np.float32)

        self.linebuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.linebuffer)
        glBufferData(GL_ARRAY_BUFFER, self.lines.nbytes, self.lines, GL_STATIC_DRAW)

    def load_texture(self):
        self.texture = None  # no texture for grid

    def render(self, MVP, View, Projection):
        self.shader.begin()
        glUniformMatrix4fv(self.mvp_id, 1, GL_FALSE, glm.value_ptr(MVP))

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.linebuffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawArrays(GL_LINES, 0, len(self.lines) // 3)

        glDisableVertexAttribArray(0)
        self.shader.end()


if __name__ == "__main__":
    window = WorldSheet()
    window.run()