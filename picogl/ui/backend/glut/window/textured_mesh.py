"""Shared textured-mesh GLUT renderer for tutorial examples (tu02, tu04, …)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from decologr import Decologr as log
from pyglm import glm

from picogl.backend.gl.api import gl_bind_texture, gl_get_active_texture0
from picogl.backend.gl.api.clear import gl_clear
from picogl.backend.gl.api.enable import gl_enable_capability_list
from picogl.backend.gl.api.shader import (gl_get_uniform_location,
                                          gl_uniform_matrix_4fv)
from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.enums.legacy.scale import gl_viewport
from picogl.backend.gl.state.shader import gl_shader_bound
from picogl.backend.glm.glm import glm_identity_matrix
from picogl.backend.glut import GLUTMouseButton, GLUTMouseState
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
from picogl.utils.mesh.protocol import MeshProtocol

_MVP_UNIFORM = "mvp_matrix"
_TEXTURE_UNIFORM = "texture0"


def rotate_model(
    rotation: RotationInteraction, model_matrix: glm.mat4
) -> glm.mat4:
    """Apply x/y drag rotation to *model_matrix* and return it."""
    model_matrix = glm.rotate(
        model_matrix, glm.radians(rotation.x), glm.vec3(1, 0, 0)
    )
    model_matrix = glm.rotate(
        model_matrix, glm.radians(rotation.y), glm.vec3(0, 1, 0)
    )
    return model_matrix


@dataclass
class TexturedRendererContext:
    """GPU state for a textured mesh draw."""

    mvp_id: int | None = None
    texture_id: int | None = None
    texture_buffer: int | None = None
    model: MeshProtocol | None = None
    projection_matrix: glm.mat4 | None = None
    view_matrix: glm.mat4 | None = None
    model_matrix: glm.mat4 | None = None
    mvp_matrix: glm.mat4 | None = None


@dataclass(frozen=True)
class TexturedRendererSpec:
    """Configuration for a textured mesh tutorial window."""

    width: int
    height: int
    title: str
    zoom_distance: float
    distance_threshold: float
    texture_path: Path
    glsl_dir: Path
    create_mesh: Callable[[bool], MeshProtocol]
    require_texture: bool = field(default=True)


class TexturedMeshRenderer(GlutRendererWindow):
    """GLUT window: textured mesh + tu02/tu04-style interaction."""

    def __init__(self, spec: TexturedRendererSpec, *args, **kwargs):
        super().__init__(
            width=spec.width,
            height=spec.height,
            title=spec.title,
            *args,
            **kwargs,
        )
        self.spec = spec
        self.context = TexturedRendererContext()
        self.shader: ShaderProgram | None = None
        if not hasattr(self, "rotation") or self.rotation is None:
            self.rotation = RotationInteraction()
        self.zoom_distance = spec.zoom_distance
        self.distance_threshold = spec.distance_threshold
        self.sync_zoom_to_context()

    def initializeGL(self) -> None:
        # GlutRendererWindow.initializeGL expects picogl.renderer.object.ObjectRenderer.
        gl_initialize_background()
        gl_enable_capability_list([GLPipelineCapability.CULL_FACE])

    def keyPressEvent(self, key, x, y) -> None:
        if key in (b"r", b"R"):
            self.rotation.reset()
            self.update_mvp()

    def mousePressEvent(self, button, state, x, y) -> None:
        if button != GLUTMouseButton.LEFT:
            return
        if state == GLUTMouseState.DOWN:
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
        if self.spec.require_texture and not self.spec.texture_path.is_file():
            raise FileNotFoundError(
                f"Texture not found: {self.spec.texture_path}"
            )

        self.context = TexturedRendererContext()
        self.sync_zoom_to_context()

        self.shader = ShaderProgram()
        self.shader.init_shader_from_shader_files(
            ShaderFiles(
                vertex="vertex.glsl",
                fragment="fragment.glsl",
                glsl_dir=self.spec.glsl_dir,
            )
        )
        if not isinstance(self.shader.program, int):
            raise TypeError("shader.program must be a GL program id (int)")

        self.context.mvp_id = gl_get_uniform_location(
            self.shader.program, _MVP_UNIFORM
        )
        self.context.texture_id = gl_get_uniform_location(
            self.shader.program, _TEXTURE_UNIFORM
        )

        texture = TextureLoader(str(self.spec.texture_path))
        self.context.texture_buffer = texture.texture_gl_id

        self.context.model = self.spec.create_mesh(texture.inversed_v_coords)
        self.context.model.upload()
        self.calc_mvp(self.width or self.spec.width, self.height or self.spec.height)

    def calc_mvp(self, width: int, height: int) -> None:
        self.sync_zoom_to_context()
        aspect = float(width) / float(max(height, 1))
        projection = ProjectionConfig(
            fovy=self.zoom_fov, aspect=aspect, near=0.1, far=1000.0
        ).matrix()
        camera = CameraParameters(eye=glm.vec3(4, 3, self.zoom_distance))
        view = camera.view_matrix()
        model = rotate_model(self.rotation, glm_identity_matrix())
        self.context.projection_matrix = projection
        self.context.view_matrix = view
        self.context.model_matrix = model
        self.context.mvp_matrix = projection * view * model

    def update_mvp(self) -> None:
        width = getattr(self, "width", None) or self.spec.width
        height = getattr(self, "height", None) or self.spec.height
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

        if self.shader is None or self.context.model is None:
            return

        with gl_shader_bound(self.shader):
            gl_uniform_matrix_4fv(
                self.context.mvp_id,
                1,
                GLBoolean.FALSE,
                glm.value_ptr(self.context.mvp_matrix),
            )
            self.bind_active_texture0()
            self.context.model.draw()
