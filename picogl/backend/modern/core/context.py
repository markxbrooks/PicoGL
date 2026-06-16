from OpenGL.GL import *  # pylint: disable=W0614
from pyglm import glm

from examples.utils.shader_loader import Shader
from examples.utils.test_window import GLWindow
from picogl.state.draw_mode import GLBufferTarget, GLUsageHint


class GObject:
    pass


class GLContext(GObject):
    def __init__(self):
        # Initialize OpenGL resource ids
        self.MVP_ID = None
        self.vertexbuffer = None
        self.colorbuffer = None

        # Transformation matrices
        self.Projection = None
        self.View = None
        self.Model = None
        self.MVP = None

    def initialize(self, shader, vertex_data, color_data):
        """Initialize the buffers and shader-related resources."""
        self.MVP_ID = glGetUniformLocation(shader.program, "MVP")

        # Vertex Buffer
        self.vertexbuffer = glGenBuffers(1)
        glBindBuffer(GLBufferTarget.ARRAY, self.vertexbuffer)
        glBufferData(
            GLBufferTarget.ARRAY,
            len(vertex_data) * 4,
            (GLfloat * len(vertex_data))(*vertex_data),
            GLUsageHint.STATIC_DRAW,
        )

        # Color Buffer
        self.colorbuffer = glGenBuffers(1)
        glBindBuffer(GLBufferTarget.ARRAY, self.colorbuffer)
        glBufferData(
            GLBufferTarget.ARRAY,
            len(color_data) * 4,
            (GLfloat * len(color_data))(*color_data),
            GLUsageHint.STATIC_DRAW,
        )

    def calculate_mvp(self, width=1920, height=1080):
        """Calculate the Model-View-Projection matrix."""
        self.Projection = glm.perspective(
            glm.radians(45.0), float(width) / float(height), 0.1, 1000.0
        )
        self.View = glm.lookAt(
            glm.vec3(4, 3, -3),  # Camera is at (4,3,-3), in World Space
            glm.vec3(0, 0, 0),  # and looks at the (0.0.0))
            glm.vec3(0, 1, 0),  # Head is up (set to 0,-1,0 to look upside-down)
        )
        self.Model = glm.mat4(1.0)

        self.MVP = self.Projection * self.View * self.Model


class Tu01Win(GLWindow):
    def __init__(self):
        super().__init__()
        self.context = GLContext()  # Create an instance of GLContext
        self.shader = None

    def initializeGL(self):
        glClearColor(0.0, 0, 0.4, 0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GLPipelineCapability.CULL_FACE)

    def init_context(self):
        self.shader = Shader()
        self.shader.initShaderFromGLSL(
            ["glsl/tu01/vertex.glsl"], ["glsl/tu01/fragment.glsl"]
        )
        self.context.initialize(self.shader, g_vertex_buffer_data, g_color_buffer_data)

    def calc_MVP(self, width=1920, height=1080):
        self.context.calculate_mvp(width, height)

    def resizeGL(self, Width, Height):
        glViewport(0, 0, Width, Height)
        self.calc_MVP(Width, Height)

    def paintGL(self):
        print("draw++")
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader.begin()
        glUniformMatrix4fv(
            self.context.MVP_ID, 1, GL_FALSE, glm.value_ptr(self.context.MVP)
        )

        glEnableVertexAttribArray(0)
        glBindBuffer(GLBufferTarget.ARRAY, self.context.vertexbuffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(1)
        glBindBuffer(GLBufferTarget.ARRAY, self.context.colorbuffer)
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
