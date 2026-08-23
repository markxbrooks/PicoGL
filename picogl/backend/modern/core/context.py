from __future__ import annotations

import os
import sys
from copy import copy
from pathlib import Path

from OpenGL.GL import *  # pylint: disable=W0614
from pyglm import glm

from picogl.backend.gl.api import (gl_bind_buffer, gl_bind_texture,
                                   gl_bind_vertex_array, gl_buffer_data,
                                   gl_draw_arrays, gl_get_active_texture0)
from picogl.backend.gl.api.buffer.generate import gl_generate_buffers
from picogl.backend.gl.api.enable import gl_enable_capability_list
from picogl.backend.gl.api.vertex.attrib_pointer import \
    gl_vertex_attrib_pointer
from picogl.backend.gl.api.vertex.enable_array import gl_enable_vertex_array
from picogl.backend.gl.api.vertex.generate_array import \
    gl_generate_vertex_array
from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.gl.enums import (GLBitMask, GLBufferTarget, GLDrawMode,
                                     GLNumeric, GLUsageHint)
from picogl.backend.glm.glm import glm_identity_matrix
from picogl.backend.modern.core.setup.lighting import gl_initialize_background
from picogl.backend.state import GLViewport
from picogl.boolean import GLBoolean
from picogl.core.camera import FOVY, CameraParameters, ProjectionConfig
from picogl.core.uniform import gl_uniform1i
from picogl.examples.data.cube_data import (g_uv_buffer_data,
                                            g_vertex_buffer_data)
from picogl.examples.utils.shader_loader import Shader
from picogl.utils.loader.texture import TextureLoader

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.ui.backend.glut.window.gl import GLWindow

_EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "examples"
_TEXTURE_PATH = _EXAMPLES_DIR / "resources" / "tu02" / "uvtemplate.tga"


class GObject:
    pass


class GLContext(GObject):
    def __init__(self):
        self.mvp_id = None
        self.texture_uniform_id = None
        self.vertexbuffer = None
        self.uvbuffer = None
        self.texture_gl_id = None
        self.vao = None

        self.Projection = None
        self.View = None
        self.Model = None
        self.mvp_matrix = None

    def initialize(
        self,
        shader: Shader,
        vertex_data: list[float],
        uv_data: list[float],
        texture_path: Path,
    ) -> None:
        """Upload position + UV buffers and load the tu02 texture."""
        self.mvp_id = glGetUniformLocation(shader.program, "mvp_matrix")
        self.texture_uniform_id = glGetUniformLocation(shader.program, "texture0")

        texture = TextureLoader(str(texture_path))
        self.texture_gl_id = texture.texture_gl_id

        uv_values = copy(uv_data)
        if texture.inversed_v_coords:
            for index in range(len(uv_values)):
                if index % 2:
                    uv_values[index] = 1.0 - uv_values[index]

        self.vertexbuffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.vertexbuffer)
        gl_buffer_data(
            target=GLBufferTarget.ARRAY,
            size=len(vertex_data) * 4,
            data=(GLfloat * len(vertex_data))(*vertex_data),
            usage_hint=GLUsageHint.STATIC_DRAW,
        )

        self.uvbuffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.uvbuffer)
        gl_buffer_data(
            target=GLBufferTarget.ARRAY,
            size=len(uv_values) * 4,
            data=(GLfloat * len(uv_values))(*uv_values),
            usage_hint=GLUsageHint.STATIC_DRAW,
        )

    def init_geometry(self) -> None:
        """Bind positions (loc 0) and UVs (loc 1) into a VAO."""
        self.vao = gl_generate_vertex_array(1)
        gl_bind_vertex_array(self.vao)

        gl_bind_buffer(GLBufferTarget.ARRAY, self.vertexbuffer)
        gl_enable_vertex_array(0)
        gl_vertex_attrib_pointer(
            index=0,
            size=3,
            num_type=GLNumeric.FLOAT,
            normalized=GLBoolean.FALSE,
            stride=0,
            offset=None,
        )

        gl_bind_buffer(GLBufferTarget.ARRAY, self.uvbuffer)
        gl_enable_vertex_array(1)
        gl_vertex_attrib_pointer(
            index=1,
            size=2,
            num_type=GLNumeric.FLOAT,
            normalized=GLBoolean.FALSE,
            stride=0,
            offset=None,
        )

        gl_bind_vertex_array(0)

    def calculate_mvp(self, width=1920, height=1080):
        """Calculate the Model-View-Projection matrix."""
        self.Projection = ProjectionConfig(
            fovy=FOVY,
            aspect=float(width) / float(max(height, 1)),
            near=ProjectionConfig().near,
            far=ProjectionConfig().far,
        ).matrix()
        camera = CameraParameters(eye=glm.vec3(4, 3, -3))
        self.View = camera.view_matrix()
        self.Model = glm_identity_matrix()
        self.mvp_matrix = self.Projection * self.View * self.Model


class Tu02Win(GLWindow):
    """Textured cube (tu02): vertex positions + UV coordinates."""

    def __init__(self):
        super().__init__(title="Tutorial 02 - Textured Cube", width=800, height=600)
        self.context = GLContext()
        self.shader: Shader | None = None

    def initializeGL(self):
        gl_initialize_background()
        gl_enable_capability_list([GLPipelineCapability.CULL_FACE])

    def init_context(self):
        self.shader = Shader()
        self.shader.initShaderFromGLSL(
            ["glsl/tu02/vertex.glsl"],
            ["glsl/tu02/fragment.glsl"],
        )
        self.context.initialize(
            self.shader,
            g_vertex_buffer_data,
            g_uv_buffer_data,
            _TEXTURE_PATH,
        )
        self.context.init_geometry()

    def calc_MVP(self, width=1920, height=1080):
        self.context.calculate_mvp(width, height)

    def resizeGL(self, width, height):
        GLViewport(width=width, height=height).apply()
        self.calc_MVP(width, height)

    def paintGL(self):
        glClear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)

        if self.shader is None or self.context.vao is None:
            return

        self.shader.begin()
        glUniformMatrix4fv(
            self.context.mvp_id,
            1,
            GLBoolean.FALSE,
            glm.value_ptr(self.context.mvp_matrix),
        )

        gl_get_active_texture0()
        gl_bind_texture(target=GL_TEXTURE_2D, tex_id=self.context.texture_gl_id)
        gl_uniform1i(self.context.texture_uniform_id, 0)

        gl_bind_vertex_array(self.context.vao)
        gl_draw_arrays(12 * 3, GLDrawMode.TRIANGLES, first=0)
        gl_bind_vertex_array(0)

        self.shader.end()


if __name__ == "__main__":
    win = Tu02Win()
    win.initializeGL()
    win.init_context()
    win.calc_MVP(win.width or 800, win.height or 600)
    win.run()
