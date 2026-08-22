from OpenGL.GL import *  # pylint: disable=W0614
from pyglm import glm
from utils.shader_loader import Shader

from picogl.backend.gl.api.enable import gl_enable_capability_list
from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.modern.core.setup.lighting import gl_initialize_background
from picogl.backend.glm.glm import glm_identity_matrix
from picogl.examples.data.cube_data import (g_color_buffer_data,
                                            g_vertex_buffer_data)
from picogl.ui.backend.glut.window.gl import GLWindow


class Tu01Win(GLWindow):
    class GLContext(object):
        pass

    def initializeGL(self):
        gl_initialize_background()
        gl_enable_capability_list([GLPipelineCapability.CULL_FACE])

    def init_context(self):
        self.context = self.GLContext()
        self.shader = shader = Shader()
        shader.initShaderFromGLSL(
            ["glsl/tu01/vertex.glsl"], ["glsl/tu01/fragment.glsl"]
        )
        self.context.MVP_ID = glGetUniformLocation(shader.program, "MVP")

        self.context.vertexbuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertexbuffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            len(g_vertex_buffer_data) * 4,
            (GLfloat * len(g_vertex_buffer_data))(*g_vertex_buffer_data),
            GL_STATIC_DRAW,
        )

        self.context.colorbuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.colorbuffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            len(g_color_buffer_data) * 4,
            (GLfloat * len(g_color_buffer_data))(*g_color_buffer_data),
            GL_STATIC_DRAW,
        )

    def calc_MVP(self, width=1920, height=1080):
        self.context.Projection = glm.perspective(
            glm.radians(45.0), float(width) / float(height), 0.1, 1000.0
        )
        self.context.View = glm.lookAt(
            glm.vec3(4, 3, -3),  # Camera is at (4,3,-3), in World Space
            glm.vec3(0, 0, 0),  # and looks at the (0.0.0))
            glm.vec3(0, 1, 0),
        )  # Head is up (set to 0,-1,0 to look upside-down)

        self.context.Model = glm_identity_matrix()

        self.context.MVP = (
            self.context.Projection * self.context.View * self.context.Model
        )

    def resizeGL(self, Width, Height):
        glViewport(0, 0, Width, Height)
        self.calc_MVP(Width, Height)

    def paintGL(self):
        print("draw++")
        # print self.context.MVP
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader.begin()
        glUniformMatrix4fv(
            self.context.MVP_ID, 1, GL_FALSE, glm.value_ptr(self.context.MVP)
        )

        gl_enableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertexbuffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        gl_enableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.colorbuffer)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawArrays(
            GL_TRIANGLES, 0, 12 * 3
        )  # 12*3 indices starting at 0 -> 12 triangles

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        self.shader.end()


if __name__ == "__main__":
    win = Tu01Win()
    win.initializeGL()
    win.init_context()
    win.run()
