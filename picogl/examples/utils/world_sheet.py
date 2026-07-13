"""
World Sheet Widget
"""

import numpy as np
from pyglm import glm

from picogl.backend.gl.api import (
    gl_bind_buffer,
    gl_buffer_data,
    gl_draw_arrays,
    gl_generate_buffers,
    gl_vertex_attrib_pointer,
)
from picogl.backend.gl.api.shader import gl_uniform_matrix_4fv
from picogl.backend.gl.api.vertex.attrib_array.generate import (
    gl_enable_vertex_attrib_array,
)
from picogl.backend.gl.enums import GLBufferTarget, GLDrawMode, GLNumeric, GLUsageHint
from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.backend.modern.renderers.mesh import ShaderMeshRenderer
from picogl.boolean import GLBoolean


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
        self.mvp_id = gl_get_uniform_location(self.shader.program, "mvp_matrix")
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

        self.line_buffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.line_buffer)
        gl_buffer_data(
            GLBufferTarget.ARRAY, self.lines.nbytes, self.lines, GLUsageHint.STATIC_DRAW
        )

    def load_texture(self):
        """load texture"""
        self.texture = None  # no texture for grid

    def render(self, mvp_matrix, view_matrix, projection_matrix):
        self.shader.begin()
        gl_uniform_matrix_4fv(
            self.mvp_id, 1, GLBoolean.FALSE, glm.value_ptr(mvp_matrix)
        )

        gl_enable_vertex_attrib_array(0)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.line_buffer)
        gl_vertex_attrib_pointer(0, 3, GLNumeric.FLOAT, GLBoolean.FALSE, 0, None)

        gl_draw_arrays(GLDrawMode.LINES, 0, len(self.lines) // 3)

        gl_disable_vertex_attrib_array(0)
        self.shader.end()

    def run(self):
        raise NotImplementedError("Needs to be implemented")


if __name__ == "__main__":
    window = WorldSheet(base_dir=".")
    window.run()
