from pathlib import Path

from OpenGL.GL import *  # pylint: disable=W0614

from picogl.core.uniform import gl_uniform1i
from picogl.globals import PROJECT_ROOT
from picogl.backend.gl.enums import GLBufferTarget
from picogl.backend.gl.enums import GLUsageHint
from picogl.ui.backend.glut.window.gl import GLWindow
from picogl.utils.loader.texture import TextureLoader
from pyglm import glm

from picogl.backend.gl.wrappers import gl_bind_texture, gl_get_active_texture0
from utils.shader_loader import Shader

g_vertex_buffer_data = [
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    1.0,
    -1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    1.0,
    -1.0,
    1.0,
    -1.0,
    1.0,
    -1.0,
    -1.0,
    -1.0,
    1.0,
    -1.0,
    -1.0,
    1.0,
    1.0,
    -1.0,
    1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    1.0,
    1.0,
    -1.0,
    1.0,
    -1.0,
    1.0,
    -1.0,
    1.0,
    -1.0,
    -1.0,
    1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    1.0,
    1.0,
    -1.0,
    -1.0,
    1.0,
    1.0,
    -1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    -1.0,
    -1.0,
    1.0,
    1.0,
    -1.0,
    1.0,
    -1.0,
    -1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    -1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    -1.0,
    -1.0,
    1.0,
    -1.0,
    1.0,
    1.0,
    1.0,
    -1.0,
    1.0,
    -1.0,
    -1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    -1.0,
    1.0,
    1.0,
    1.0,
    -1.0,
    1.0,
]
g_uv_buffer_data = [
    0.000059,
    1.0 - 0.000004,
    0.000103,
    1.0 - 0.336048,
    0.335973,
    1.0 - 0.335903,
    1.000023,
    1.0 - 0.000013,
    0.667979,
    1.0 - 0.335851,
    0.999958,
    1.0 - 0.336064,
    0.667979,
    1.0 - 0.335851,
    0.336024,
    1.0 - 0.671877,
    0.667969,
    1.0 - 0.671889,
    1.000023,
    1.0 - 0.000013,
    0.668104,
    1.0 - 0.000013,
    0.667979,
    1.0 - 0.335851,
    0.000059,
    1.0 - 0.000004,
    0.335973,
    1.0 - 0.335903,
    0.336098,
    1.0 - 0.000071,
    0.667979,
    1.0 - 0.335851,
    0.335973,
    1.0 - 0.335903,
    0.336024,
    1.0 - 0.671877,
    1.000004,
    1.0 - 0.671847,
    0.999958,
    1.0 - 0.336064,
    0.667979,
    1.0 - 0.335851,
    0.668104,
    1.0 - 0.000013,
    0.335973,
    1.0 - 0.335903,
    0.667979,
    1.0 - 0.335851,
    0.335973,
    1.0 - 0.335903,
    0.668104,
    1.0 - 0.000013,
    0.336098,
    1.0 - 0.000071,
    0.000103,
    1.0 - 0.336048,
    0.000004,
    1.0 - 0.671870,
    0.336024,
    1.0 - 0.671877,
    0.000103,
    1.0 - 0.336048,
    0.336024,
    1.0 - 0.671877,
    0.335973,
    1.0 - 0.335903,
    0.667969,
    1.0 - 0.671889,
    1.000004,
    1.0 - 0.671847,
    0.667979,
    1.0 - 0.335851,
]


class Tu01Win(GLWindow):
    class GLContext(object):
        pass

    def init_opengl(self):
        glClearColor(0.0, 0, 0.4, 0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def init_context(self):
        self.context = self.GLContext()

        # vertex = glGenVertexArrays(1) # pylint: disable=W0612
        # glBindVertexArray(vertex)

        self.shader = shader = Shader()
        shader.initShaderFromGLSL(
            ["glsl/tu02/vertex.glsl"], ["glsl/tu02/fragment.glsl"]
        )

        self.context.mvp_id = glGetUniformLocation(shader.program, "MVP")
        self.context.texture_id = glGetUniformLocation(shader.program, "texture0")

        texture = TextureLoader(Path(PROJECT_ROOT) / "examples" / "resources" / "tu02" / "uvtemplate.tga")

        self.context.textureGLID = texture.texture_gl_id

        self.context.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertex_buffer)
        glBufferData(
            GLBufferTarget.ARRAY,
            len(g_vertex_buffer_data) * 4,
            (GLfloat * len(g_vertex_buffer_data))(*g_vertex_buffer_data),
            GLUsageHint.STATIC_DRAW,
        )

        if texture.inversed_v_coords:
            for index in range(0, len(g_uv_buffer_data)):
                if index % 2:
                    g_uv_buffer_data[index] = 1.0 - g_uv_buffer_data[index]

        self.context.uv_buffer = glGenBuffers(1)
        glBindBuffer(GLBufferTarget.ARRAY, self.context.uv_buffer)
        glBufferData(
            GLBufferTarget.ARRAY,
            len(g_uv_buffer_data) * 4,
            (GLfloat * len(g_uv_buffer_data))(*g_uv_buffer_data),
            GLUsageHint.STATIC_DRAW,
        )

    def _init_geometry(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # positions
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertex_buffer)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # UVs
        glBindBuffer(GL_ARRAY_BUFFER, self.context.uv_buffer)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

        # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.context.indices)

        glBindVertexArray(0)

    def calc_MVP(self, width=1920, height=1080):
        self.context.Projection = glm.perspective(
            glm.radians(45.0), float(width) / float(height), 0.1, 1000.0
        )
        self.context.View = glm.lookAt(
            glm.vec3(4, 3, -3),  # Camera is at (4,3,-3), in World Space
            glm.vec3(0, 0, 0),  # and looks at the (0.0.0))
            glm.vec3(0, 1, 0),
        )  # Head is up (set to 0,-1,0 to look upside-down)
        # fixed Cube Size
        self.context.Model = glm.mat4(1.0)
        # print(self.context.Model
        self.context.mvp_matrix = (
            self.context.Projection * self.context.View * self.context.Model
        )
        self.context.mvp_matrix = (
                self.context.Projection * self.context.View * self.context.Model
        )

    def resize(self, Width, Height):
        glViewport(0, 0, Width, Height)
        self.calc_MVP(Width, Height)

    def on_mousemove(self, x: int, y: int) -> None:
        """Handle mouse movement."""
        delta_x = self.lastX - x
        delta_y = self.lastY - y

        if self.mouse_mode == MouseMode.ROTATE:
            self.lastX, self.lastY = x, y
            self.look_upward(delta_y * 0.01)
            self.turn(delta_x * 0.01)
            self.update_callback()
        elif self.mouse_mode == MouseMode.PAN:
            self.lastX, self.lastY = x, y
            self.move_up(-0.5 * delta_x)
            self.update_callback()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader.begin()

        glUniformMatrix4fv(
            self.context.mvp_id,
            1,
            GL_FALSE,
            glm.value_ptr(self.context.mvp_matrix),
        )

        self._bind_texture()

        glBindVertexArray(self.vao)

        """glDrawElements(
            GL_TRIANGLES,
            self.context.indices_size,
            GL_UNSIGNED_SHORT,
            None
        )"""
        glDrawArrays(GL_TRIANGLES, 0, 12 * 3)
        glBindVertexArray(0)

        self.shader.end()

    def _bind_texture(self):
        gl_get_active_texture0()
        gl_bind_texture(target=GL_TEXTURE_2D, tex_id=self.context.textureGLID)
        gl_uniform1i(self.context.texture_id, 0)

    def ogl_draw(self):
        print("draw++")
        # print(self.context.MVP)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader.begin()
        glUniformMatrix4fv(
            self.context.mvp_id, 1, GL_FALSE, glm.value_ptr(self.context.mvp_matrix)
        )

        bind_active_texture0()

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertexbuffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.uvbuffer)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

        glDrawArrays(
            GL_TRIANGLES, 0, 12 * 3
        )  # 12*3 indices starting at 0 -> 12 triangles

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        self.shader.end()


if __name__ == "__main__":
    win = Tu01Win()
    win.init_opengl()
    win.init_context()
    win._init_geometry()
    win.calc_MVP()
    win.run()
