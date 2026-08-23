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

from OpenGL.GL import GLfloat, GLushort
from OpenGL.GLUT import GLUT_DOWN, GLUT_LEFT_BUTTON
from decologr import Decologr as log
from pyglm import glm

from picogl.backend.gl.api import (
    gl_bind_buffer,
    gl_bind_texture,
    gl_buffer_data,
    gl_draw_elements,
    gl_generate_buffers,
    gl_get_active_texture0,
)
from picogl.backend.gl.api.clear import gl_clear
from picogl.backend.gl.api.enable import gl_enable_capability_list
from picogl.backend.gl.api.shader import gl_get_uniform_location, gl_uniform_matrix_4fv
from picogl.backend.gl.api.vertex.attrib_array.disable import (
    gl_disable_vertex_attrib_array,
)
from picogl.backend.gl.api.vertex.attrib_array.generate import (
    gl_enable_vertex_attrib_array,
)
from picogl.backend.gl.api.vertex.attrib_array.pointer import gl_vertex_attrib_pointer
from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.gl.enums import (
    GLBitMask,
    GLBufferTarget,
    GLDrawMode,
    GLNumeric,
    GLUsageHint,
)
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
from picogl.utils.loader.object import ObjectLoader
from picogl.utils.loader.texture import TextureLoader

_EXAMPLES_DIR = Path(__file__).resolve().parent
_DEFAULT_MESH = _EXAMPLES_DIR / "resources" / "tu04" / "suzanne.obj"
_DEFAULT_TEXTURE = _EXAMPLES_DIR / "resources" / "tu04" / "uvmap.DDS"
_GLSL_DIR = _EXAMPLES_DIR / "glsl" / "tu04"


def _flip_texcoord_v(texcoords: list[float]) -> list[float]:
    """Invert V for DDS/top-left origin (TextureLoader.inversed_v_coords)."""
    flipped = list(texcoords)
    for i in range(1, len(flipped), 2):
        flipped[i] = 1.0 - flipped[i]
    return flipped


@contextmanager
def gl_bound_vertex_attrib_arrays(vertex_attrib_arrays: list[int]):
    """Enable vertex attrib arrays for the block, then disable them."""
    try:
        for vertex_attrib_array in vertex_attrib_arrays:
            gl_enable_vertex_attrib_array(vertex_attrib_array)
        yield
    finally:
        for vertex_attrib_array in reversed(vertex_attrib_arrays):
            gl_disable_vertex_attrib_array(vertex_attrib_array)


def gl_bind_array_buffer(buffer, index: int = 0, size: int = 3, stride: int = 0) -> None:
    """Bind an ARRAY buffer and set its vertex attrib pointer."""
    gl_bind_buffer(GLBufferTarget.ARRAY, buffer)
    gl_vertex_attrib_pointer(index, size, GLNumeric.FLOAT, GLBoolean.FALSE, stride, None)


def gl_bind_elements(index_buffer, size: int) -> None:
    """Bind ELEMENT buffer and draw triangles (ushort indices)."""
    gl_bind_buffer(GLBufferTarget.ELEMENT, index_buffer)
    # PicoGL: (index_count, dtype, mode) — not raw GL (mode, count, type).
    gl_draw_elements(size, GLNumeric.UNSIGNED_SHORT, GLDrawMode.TRIANGLES)


def gl_upload_float_buffer(
    data: list[float],
    buffer_target: GLBufferTarget = GLBufferTarget.ARRAY,
) -> None:
    """Upload float vertex/attribute data to the bound buffer."""
    gl_buffer_data(
        buffer_target,
        len(data) * 4,
        (GLfloat * len(data))(*data),
        GLUsageHint.STATIC_DRAW,
    )


def gl_upload_ushort_buffer(
    data: list[int],
    buffer_target: GLBufferTarget = GLBufferTarget.ELEMENT,
) -> None:
    """Upload unsigned-short index data to the bound element buffer."""
    gl_buffer_data(
        buffer_target,
        len(data) * 2,
        (GLushort * len(data))(*data),
        GLUsageHint.STATIC_DRAW,
    )


class MeshObject:
    """Local OBJ mesh with GPU buffer upload helpers."""

    def __init__(self, path: Path | str = _DEFAULT_MESH):
        self.path = Path(path)
        self.vertices: list[float] | None = None
        self.texcoords: list[float] | None = None
        self.indices: list[int] | None = None
        self.vertex_buffer: int | None = None
        self.uv_buffer: int | None = None
        self.index_buffer: int | None = None
        self.indices_size: int = 0

    def load_mesh(self):
        if not self.path.is_file():
            raise FileNotFoundError(f"OBJ mesh not found: {self.path}")
        return ObjectLoader(str(self.path)).to_single_index_style()

    def get_mesh(self, *, flip_v: bool = False) -> MeshObject:
        mesh = self.load_mesh()
        self.vertices = mesh.vertices
        self.texcoords = (
            _flip_texcoord_v(mesh.texcoords) if flip_v else list(mesh.texcoords)
        )
        self.indices = mesh.indices
        self.indices_size = len(self.indices)
        return self

    def _upload_vertices(self) -> None:
        gl_upload_float_buffer(self.vertices)

    def _upload_texcoords(self) -> None:
        gl_upload_float_buffer(self.texcoords)

    def _upload_indices(self) -> None:
        # Must be GLushort to match gl_draw_elements(..., UNSIGNED_SHORT, ...).
        gl_upload_ushort_buffer(self.indices)

    def upload(self) -> None:
        self.vertex_buffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.vertex_buffer)
        self._upload_vertices()

        self.uv_buffer = gl_generate_buffers(1)
        gl_bind_buffer(GLBufferTarget.ARRAY, self.uv_buffer)
        self._upload_texcoords()

        self.index_buffer = gl_generate_buffers(1)
        # Draw-element count — not the GL buffer name from gl_generate_buffers.
        self.indices_size = len(self.indices)
        gl_bind_buffer(GLBufferTarget.ELEMENT, self.index_buffer)
        self._upload_indices()

    def draw(self) -> None:
        """Draw the mesh."""
        with gl_bound_vertex_attrib_arrays([0, 1]):
            self._draw_vertices(index=0)
            self._draw_uvs(index=1)
            self._draw_indices()

    def _draw_vertices(self, index: int = 0) -> None:
        gl_bind_array_buffer(self.vertex_buffer, index=index)

    def _draw_uvs(self, index: int = 1) -> None:
        gl_bind_array_buffer(self.uv_buffer, index=index, size=2, stride=0)

    def _draw_indices(self) -> None:
        gl_bind_elements(index_buffer=self.index_buffer, size=self.indices_size)


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
        title: str = "Tutorial 04 - Textured Model",
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
        self.context.model = MeshObject().get_mesh(
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
