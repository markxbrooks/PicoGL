from OpenGL.GL import *  # pylint: disable=W0614
from pyglm import glm

from picogl.backend.gl.api import (gl_bind_buffer, gl_buffer_data,
                                   gl_disable_vertex_array, gl_draw_arrays)
from picogl.backend.gl.api.buffer.generate import gl_generate_buffers
from picogl.backend.gl.api.enable import gl_enable_capability_list
from picogl.backend.gl.api.enable_vertex_array import gl_enable_vertex_array
from picogl.backend.gl.api.vertex.attrib_pointer import \
    gl_vertex_attrib_pointer
from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.modern.core.setup.lighting import gl_initialize_background
from picogl.backend.gl.enums import (GLBitMask, GLBufferTarget, GLNumeric,
                                     GLUsageHint)
from picogl.backend.glm.glm import glm_identity_matrix
from picogl.backend.state import GLViewport
from picogl.core.camera import FOVY, ProjectionConfig
from picogl.boolean import GLBoolean
from picogl.examples.utils.shader_loader import Shader
from picogl.examples.utils.test_window import GLWindow


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
        self.vertexbuffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.vertexbuffer)
        gl_buffer_data(
            target=GLBufferTarget.ARRAY,
            size=len(vertex_data) * 4,
            data=(GLfloat * len(vertex_data))(*vertex_data),
            usage_hint=GLUsageHint.STATIC_DRAW,
        )

        # Color Buffer
        self.colorbuffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.colorbuffer)
        gl_buffer_data(
            target=GLBufferTarget.ARRAY,
            size=len(color_data) * 4,
            data=(GLfloat * len(color_data))(*color_data),
            usage_hint=GLUsageHint.STATIC_DRAW,
        )

    def calculate_mvp(self, width=1920, height=1080):
        """Calculate the Model-View-Projection matrix."""
        self.Projection = glm.perspective(
            glm.radians(FOVY),
            float(width) / float(height),
            ProjectionConfig.near,
            ProjectionConfig.far,
        )
        self.View = glm.lookAt(
            glm.vec3(4, 3, -3),  # Camera is at (4,3,-3), in World Space
            glm.vec3(0, 0, 0),  # and looks at the (0.0.0))
            glm.vec3(0, 1, 0),  # Head is up (set to 0,-1,0 to look upside-down)
        )
        self.Model = glm_identity_matrix()

        self.MVP = self.Projection * self.View * self.Model


class Tu01Win(GLWindow):
    def __init__(self):
        super().__init__()
        self.context = GLContext()  # Create an instance of GLContext
        self.shader = None

    def initializeGL(self):
        gl_initialize_background()
        gl_enable_capability_list([GLPipelineCapability.CULL_FACE])

    def init_context(self):
        self.shader = Shader()
        self.shader.initShaderFromGLSL(
            ["glsl/tu01/vertex.glsl"], ["glsl/tu01/fragment.glsl"]
        )
        self.context.initialize(self.shader, g_vertex_buffer_data, g_color_buffer_data)

    def calc_MVP(self, width=1920, height=1080):
        self.context.calculate_mvp(width, height)

    def resizeGL(self, Width, Height):
        GLViewport(width=Width, height=Height).apply()
        self.calc_MVP(Width, Height)

    def paintGL(self):
        print("draw++")
        glClear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)

        self.shader.begin()
        glUniformMatrix4fv(
            self.context.MVP_ID, 1, GLBoolean.FALSE, glm.value_ptr(self.context.MVP)
        )

        gl_enable_vertex_array(0)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.context.vertexbuffer)
        gl_vertex_attrib_pointer(
            index=0,
            size=3,
            num_type=GLNumeric.FLOAT,
            normalized=GLBoolean.FALSE,
            stride=0,
            offset=None,
        )

        gl_enable_vertex_array(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.context.colorbuffer)
        gl_vertex_attrib_pointer(
            index=1,
            size=3,
            num_type=GLNumeric.FLOAT,
            normalized=GLBoolean.FALSE,
            stride=0,
            offset=None,
        )

        gl_draw_arrays(12 * 3, GL_TRIANGLES, first=0)

        gl_disable_vertex_array(0)
        gl_disable_vertex_array(1)
        self.shader.end()


if __name__ == "__main__":
    win = Tu01Win()
    win.initializeGL()
    win.init_context()
    win.run()
