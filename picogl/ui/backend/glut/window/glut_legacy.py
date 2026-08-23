import numpy as np
from decologr import Decologr as log
from decologr import setup_logging
from pyglm import glm

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.backend.gl.backend import GLBackend
from picogl.backend.gl.task.gl_init import legacy_init_gl_list, paint_gl_list
from picogl.backend.glm.glm import glm_identity_matrix
from picogl.backend.modern.core.camera.projection_state import \
    GLMProjectionState
from picogl.backend.opengl import LegacyBinding
from picogl.backend.state import GLViewport
from picogl.core.camera import ProjectionConfig
from picogl.renderer import GLResourceRegistry
from picogl.renderer.object import ObjectRenderer
from picogl.ui.backend.glut.mouse import RotationInteraction
from picogl.ui.backend.glut.window.gl import GLWindow


class GlutRendererWindow(GLWindow):
    """Glut Rendered Window"""

    def __init__(
        self,
        width,
        height,
        title: str = None,
        context: GLResourceRegistry = None,
        *args,
        **kwargs,
    ):
        super().__init__(title=title, *args, **kwargs)
        self.context = GLResourceRegistry() if context is None else context
        self.title = title
        self.renderer = ObjectRenderer(context, data=None)
        self.viewport = GLViewport(width=width, height=height)
        self.projection_config = ProjectionConfig()
        self.projection = GLMProjectionState()
        self.width = width
        self.height = height
        self.rotation = RotationInteraction()
        setup_logging()
        self.zoom_fov: float = ProjectionConfig.fovy
        self.zoom_distance: float = 10.0  # camera backwards in Z
        self.distance_threshold: float = 5.0
        self.sync_zoom_to_context()
        self.backend = GLBackend(binding=LegacyBinding())

    def initializeGL(self):
        """Initial OpenGL configuration."""
        log.message("Initializing OpenGL context...")
        self.backend.execute_gl_tasks(legacy_init_gl_list)
        self.renderer.initialize_shaders()
        self.renderer.initialize()

    def calculate_mvp_matrix(
            self,
            width: int | None = None,
            height: int | None = None,
    ) -> None:
        """Calculate the model-view-projection matrix."""
        width = self.viewport.width if width is None else width
        height = self.viewport.height if height is None else height

        camera = self.camera_config
        config = camera.projection.with_aspect(
            float(width) / float(max(height, 1))
        )
        self.projection.apply(config)
        self.context.projection = self.projection.matrix

        camera_params = camera.camera_parameters()
        self.context.eye = camera_params.eye
        self.context.center = camera_params.center
        self.context.up = camera_params.up
        self.context.view = camera_params.view_matrix()

        self.context.model_matrix = glm_identity_matrix()

        self.context.eye_np = np.array(
            self.context.eye.to_list(),
            dtype=np.float32,
        )

        self.context.mvp_matrix = (
                self.context.projection
                * self.context.view
                * self.context.model_matrix
        )

    def resizeGL(self, width, height):
        """resizeGL"""
        log.message(f"Resizing viewport to {width}x{height}...")
        self.viewport.width = width
        self.viewport.height = height
        self.width = width
        self.height = height
        self.viewport.apply()
        self.calculate_mvp_matrix(self.viewport.width, self.viewport.height)

    def paintGL(self):
        """paintGL"""
        self.backend.execute_gl_tasks(paint_gl_list)
        self.renderer.render()

    def update_mvp(self):
        """Base perspective matrix from your existing method"""
        self.sync_zoom_to_context()
        width, height = self.get_size()
        self.calculate_mvp_matrix(width, height)
        # Apply rotations
        rotation_matrix = glm.rotate(
            glm_identity_matrix(),
            glm.radians(self.rotation.x),
            glm.vec3(1, 0, 0),
        )
        rotation_matrix = glm.rotate(
            rotation_matrix,
            glm.radians(self.rotation.y),
            glm.vec3(0, 1, 0),
        )
        self.context.mvp_matrix = self.context.mvp_matrix * rotation_matrix
        self.update()  # Trigger repaint

    def mousePressEvent(self, button, state, x, y):
        """mousePressEvent"""
        if state == 0:  # Mouse button pressed
            self.rotation.press(x, y)
        else:
            self.rotation.release()

    def mouseMoveEvent(self, x, y):
        """mouseMoveEvent"""
        if self.rotation.drag(x, y) is None:
            return
        self.update_mvp()

    def get_size(self):
        return self.viewport.size


if __name__ == "__main__":
    win = GlutRendererWindow(width=1024, height=768)
    win.run()
