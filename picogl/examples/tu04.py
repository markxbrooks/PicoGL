"""
Tutorial 04 — Textured Suzanne (PicoGL).

Uses PicoGL loaders, shaders, and GL wrappers throughout.
Left-drag rotates, wheel zooms, R resets.
"""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path

# freeglut creates GLX contexts; under Wayland PyOpenGL may pick EGL first.
# Must be set before any OpenGL / picogl import.
if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
import picogl.ui.backend.glut.prefer_apple_glut  # noqa: F401

from OpenGL.GLUT import GLUT_DOWN, GLUT_LEFT_BUTTON
from decologr import Decologr as log
from pyglm import glm

from picogl.backend.gl.api import gl_bind_texture, gl_get_active_texture0
from picogl.backend.gl.api.clear import gl_clear
from picogl.backend.gl.api.enable import gl_enable_capability_list
from picogl.backend.gl.api.shader import gl_get_uniform_location, gl_uniform_matrix_4fv
from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.enums.legacy.scale import gl_viewport
from picogl.backend.glm.glm import glm_identity_matrix
from picogl.backend.modern.core.setup.lighting import gl_initialize_background
from picogl.backend.modern.core.shader.files import ShaderFiles
from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.boolean import GLBoolean
from picogl.core.camera import CameraParameters, ProjectionConfig
from picogl.core.uniform import gl_uniform1i
from picogl.texture.gltexture import GLTexture
from picogl.ui.backend.glut.mouse import RotationInteraction
from picogl.ui.backend.glut.window.glut import GlutRendererWindow
from picogl.utils.loader.texture import TextureLoader
from picogl.utils.mesh import MeshObject

_EXAMPLES_DIR = Path(__file__).resolve().parent
_DEFAULT_MESH = _EXAMPLES_DIR / "resources" / "tu04" / "suzanne.obj"
_DEFAULT_TEXTURE = _EXAMPLES_DIR / "resources" / "tu04" / "uvmap.DDS"
_GLSL_DIR = _EXAMPLES_DIR / "glsl" / "tu04"


def rotate_model(rotation: RotationInteraction, model_matrix):
    """Apply x/y drag rotation to *model_matrix* and return it."""
    model_matrix = glm.rotate(model_matrix, glm.radians(rotation.x), glm.vec3(1, 0, 0))
    model_matrix = glm.rotate(model_matrix, glm.radians(rotation.y), glm.vec3(0, 1, 0))
    return model_matrix


@contextmanager
def gl_shader_bound(shader: ShaderProgram):
    """Bind *shader* for the duration of the with-block."""
    try:
        shader.begin()
        yield
    finally:
        shader.end()


class ObjectRendererExample(GlutRendererWindow):
    """Textured Suzanne tutorial window."""

    class GLContext:
        def __init__(self) -> None:
            self.mvp_id: int | None = None
            self.texture_id: int | None = None
            self.texture_buffer: int | None = None
            self.model: MeshObject | None = None
            self.projection_matrix = None
            self.view_matrix = None
            self.model_matrix = None
            self.mvp_matrix = None

    def __init__(
        self,
        width: int = 400,
        height: int = 300,
        title: str = "Suzanne - Textured Model",
        *args,
        **kwargs,
    ):
        super().__init__(width=width, height=height, title=title, *args, **kwargs)
        self.shader: ShaderProgram | None = None
        if not hasattr(self, "rotation") or self.rotation is None:
            self.rotation = RotationInteraction()
        self.zoom_distance = 5.0
        self.distance_threshold = 2.0
        self.sync_zoom_to_context()

    def initializeGL(self) -> None:
        # Avoid GlutRendererWindow.initializeGL — it expects an ObjectRenderer.
        gl_initialize_background()
        gl_enable_capability_list([GLPipelineCapability.CULL_FACE])

    def keyPressEvent(self, key, x, y) -> None:
        if key in (b"r", b"R"):
            self.rotation.reset()
            self.update_mvp()

    def mousePressEvent(self, button, state, x, y) -> None:
        if button != GLUT_LEFT_BUTTON:
            return
        if state == GLUT_DOWN:
            self.rotation.press(x, y)
        else:
            self.rotation.release()

    def mouseMoveEvent(self, x, y) -> None:
        if self.rotation.drag(x, y) is None:
            return
        self.rotation.clamp_x()
        self.update_mvp()

    def bind_active_texture0(self) -> None:
        gl_get_active_texture0()
        gl_bind_texture(self.context.texture_buffer, GLTexture.TEXTURE_2D)
        gl_uniform1i(self.context.texture_id, 0)

    def initialize(self) -> None:
        self.context = self.GLContext()
        self.sync_zoom_to_context()

        self.shader = ShaderProgram()
        self.shader.init_shader_from_shader_files(
            ShaderFiles(
                vertex="vertex.glsl",
                fragment="fragment.glsl",
                glsl_dir=_GLSL_DIR,
            )
        )
        if not isinstance(self.shader.program, int):
            raise TypeError("shader.program must be a GL program id (int)")

        self.context.mvp_id = gl_get_uniform_location(self.shader.program, "MVP")
        self.context.texture_id = gl_get_uniform_location(
            self.shader.program, "texture0"
        )

        texture = TextureLoader(str(_DEFAULT_TEXTURE))
        self.context.texture_buffer = texture.texture_gl_id
        self.context.model = MeshObject(_DEFAULT_MESH).get_mesh(
            flip_v=bool(texture.inversed_v_coords)
        )
        self.context.model.upload()
        self.calc_mvp(self.width or 400, self.height or 300)

    def calc_mvp(self, width: int = 1920, height: int = 1080) -> None:
        self.sync_zoom_to_context()
        aspect = float(width) / float(max(height, 1))
        self.context.projection_matrix = ProjectionConfig(
            fovy=self.zoom_fov, aspect=aspect, near=0.1, far=1000.0
        ).matrix()
        camera = CameraParameters(eye=glm.vec3(4, 3, self.zoom_distance))
        self.context.view_matrix = camera.view_matrix()

        self.context.model_matrix = rotate_model(self.rotation, glm_identity_matrix())
        self.context.mvp_matrix = (
            self.context.projection_matrix
            * self.context.view_matrix
            * self.context.model_matrix
        )

    def update_mvp(self) -> None:
        """Refresh MVP from zoom/viewport and request a redraw."""
        width = getattr(self, "width", None) or 400
        height = getattr(self, "height", None) or 300
        viewport = getattr(self, "viewport", None)
        if viewport is not None:
            width = getattr(viewport, "width", None) or width
            height = getattr(viewport, "height", None) or height
        self.calc_mvp(width, height)
        self.update()

    def resizeGL(self, width, height) -> None:
        log.message("resizeGL")
        self.width = width
        self.height = height
        gl_viewport(0, 0, width, height)
        self.calc_mvp(width, height)

    def paintGL(self) -> None:
        gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)

        with gl_shader_bound(self.shader):
            gl_uniform_matrix_4fv(
                self.context.mvp_id,
                1,
                GLBoolean.FALSE,
                glm.value_ptr(self.context.mvp_matrix),
            )
            self.bind_active_texture0()
            self.context.model.draw()


if __name__ == "__main__":
    win = ObjectRendererExample(width=400, height=300)
    win.initializeGL()
    win.initialize()
    win.run()
