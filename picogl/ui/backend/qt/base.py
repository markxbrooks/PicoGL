"""
GLBase Qt Widget
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from backend.gl.api.matrix import gl_matrix_mode
from backend.gl.enums.legacy.scale import gl_load_identity, gl_rotatef
from decologr import Decologr as log
from OpenGL.raw.GL.ARB.viewport_array import GL_VIEWPORT
from OpenGL.raw.GL.VERSION.GL_1_0 import glLoadIdentity, glMatrixMode
from picogl.backend.geometry.factory import LegacyBinding, ModernBinding
from picogl.backend.gl.api import gl_get_integerv
from picogl.backend.gl.api.error import gl_check_errors
from picogl.backend.gl.backend import GLBackend
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.mode import GLMode
from picogl.backend.gl.task.gl_init import legacy_init_gl_list, modern_init_gl_list
from picogl.backend.legacy.core.camera.lighting import set_background_color
from picogl.backend.legacy.core.camera.projection_state import GLUProjectionState
from picogl.backend.legacy.core.camera.setup import calculate_aspect_ratio
from picogl.backend.modern.core.camera.projection_state import GLMProjectionState
from picogl.core.camera import ProjectionConfig
from picogl.core.viewport import Viewport
from PySide6.QtGui import QMouseEvent, QOpenGLFunctions, Qt, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget


@dataclass
class MvpParameters:
    """MVP Parameters"""

    rotation_x = 0.0
    rotation_y = 0.0
    pan_x = 0.0
    pan_y = 0.0

    def initialize(self):
        self.x = 0.0
        self.y = 0.0
        self.pan_x = 0.0
        self.pan_y = 0.0


@dataclass
class CameraParameters:
    """camera parameters"""

    rotation_x_axis = None
    rotation_y_axis = None
    rotation_z_axis = None
    translation_x_axis = None
    translation_y_axis = None
    translation_zoom = None
    rotation: np.ndarray = field(
        default_factory=lambda: np.array([0.0, 0.0, 0.0], dtype=np.float32)
    )  # x, y, z
    translation: np.ndarray = field(
        default_factory=lambda: np.array([0.0, 0.0], dtype=np.float32)
    )  # x_pan, y_pan
    # zoom: CameraParameterZoom = field(default_factory=CameraParameterZoom)

    def initialize(self):
        self.rotation_x_axis = 0.0
        self.rotation_y_axis = 0.0
        self.rotation_z_axis = 0.0
        self.translation_x_axis = 0.0
        self.translation_y_axis = 0.0
        self.translation_zoom = 0.0

@dataclass
class ScreenParameters:
    """Screen Parameters Base class for rotation and translation"""
    x = 0.0
    y = 0.0

    def initialize(self):
        self.x = 0.0
        self.y = 0.0

class GLTranslation:
    """Translation Parameters"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def apply(self):
        gl_translate_f(self.x, self.y, self.z)

    def _apply_zoom(self, value: float = 0.01):
        gl_translate_f(self.translation.x, self.translation.y, value)


@dataclass
class GLZoom:
    """Zoom parameters."""

    value: float = -5.0

    def apply(self):
        gl_translate_f(0.0, 0.0, self.value)


class RotationParameters(ScreenParameters):
    """Rotation Parameters"""

@dataclass
class GLRotation:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def apply(self):
        gl_rotatef(self.x, 1.0, 0.0, 0.0)
        gl_rotatef(self.y, 0.0, 1.0, 0.0)
        gl_rotatef(self.z, 0.0, 0.0, 1.0)


class GLBase(QOpenGLWidget, QOpenGLFunctions):
    """
    OpenGL Qt Widget
    """

    def __init__(
        self, parent: Optional[QWidget] = None, gl_mode: GLMode = GLMode.LEGACY
    ):
        """
        constructor

        :param parent: QWidget
        """
        super().__init__(parent)
        if gl_mode:
            gl_mode = GLMode.LEGACY
        elif not gl_mode:
            gl_mode = GLMode.MODERN
        self.aspect_ratio = None
        self.gl_mode = gl_mode
        self.last_mouse_pos = None
        self.zoom_value = None
        self.mvp_parameters = MvpParameters()
        self.camera_parameters = CameraParameters()
        self.projection_config = ProjectionConfig()
        if self.gl_mode == GLMode.MODERN:
            self.projection = GLMProjectionState()
        else:
            self.projection = GLUProjectionState()
        binding = ModernBinding() if self.gl_mode == GLMode.MODERN else LegacyBinding()
        self.backend = GLBackend(binding)

        # Set up view
        self.zoom = 1.0
        self.rotation = GLRotation()
        self.translation = GLTranslation()

    @property
    def rotation_x(self):
        return self.rotation.x

    @rotation_x.setter
    def rotation_x(self, value):
        self.rotation.x = value
        self.update()

    @property
    def rotation_y(self):
        return self.rotation.y

    @rotation_y.setter
    def rotation_y(self, value):
        self.rotation.y = value
        self.update()

    @property
    def translation_x(self):
        return self.translation.x

    @translation_x.setter
    def translation_x(self, value):
        self.translation.x = value
        self.update()

    @property
    def translation_y(self):
        return self.translation.y

    @translation_y.setter
    def translation_y(self, value):
        self.translation.y = value
        self.update()

    def initializeGL(self):
        """
        initializeGL

        Initializes the OpenGL rendering context for this widget.

        This includes:
        - Enabling depth testing and multisampling
        - Configuring blending for transparency
        - Initializing lighting and material properties
        - Setting the viewport to match widget size
        - Clearing any legacy buffer state

        Called automatically by Qt when the gl context is first created.
        """
        # Viewport setup
        self.backend.frame.set_viewport(Viewport(0, 0, self.width(), self.height()))
        init_list = (
            modern_init_gl_list
            if self.gl_mode == GLMode.MODERN
            else legacy_init_gl_list
        )
        self.backend.execute_gl_tasks(init_list)

    def initialize(self):
        self.initialize_rotation()
        self.zoom = 20.0

    def initialize_rotation(self):
        self.rotation.initialize()

    def resizeGL(self, w: int, h: int) -> None:
        """
        resizeGL(w, h)

        Handles resizing the OpenGL viewport and updates the projection matrix.

        :param w: int - New width of the OpenGL widget
        :param h: int - New height of the OpenGL widget
        """
        if not self.context().isValid():
            log.warning("OpenGL context invalid during resize. Skipping resizeGL.")
            return
        # Prevent division by zero
        h = max(h, 1)
        # Update viewport
        self.backend.frame.set_viewport(Viewport(0, 0, w, h))
        self.aspect_ratio = calculate_aspect_ratio(h, w)
        self.projection.apply(self.projection_config.with_aspect(self.aspect_ratio))
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)
        gl_load_identity()
        # Update camera matrix using legacy pipeline
        log.message(
            f"✅ Resized OpenGL viewport to {w}x{h}, aspect {self.aspect_ratio:.2f}"
        )

    def update_mvp(self) -> None:
        """Update model-view-projection matrix."""

    def paintGL(self):
        """
        paintGL

        :return: None
        OpenGL rendering entry point. Calls the appropriate rendering method based g.
        Modern OpenGL rendering entry point.
        """
        gl_check_errors()
        width, height = self.width(), self.height()
        self.backend.prepare_viewport(width, height)
        set_background_color(show_white_background=False)  # Then set visuals
        gl_check_errors()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        mousePressEvent

        :param event: QMouseEvent
        Handle mouse press events, including atom picking and coordinate un-projection.
        """
        # log.message("Mouse press")
        self.last_mouse_pos = event.position()

        if event.button() != Qt.LeftButton:
            return

        x, y = event.x(), event.y()
        log.message(f"Clicked position: x={x}, y={y}")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        mouseMoveEvent

        :param event: QMouseEvent
        Handle mouse movement for X/Y axis rotation.
        """
        if self.last_mouse_pos is None:
            return
        delta = event.position() - self.last_mouse_pos
        buttons = event.buttons()

        if buttons & Qt.LeftButton:
            self.mvp_parameters.rotation_x += delta.x() * 0.5
            self.mvp_parameters.rotation_y += delta.y() * 0.5
        elif buttons & Qt.RightButton:
            self.mvp_parameters.pan_x += delta.x() * 0.01
            self.mvp_parameters.pan_y -= delta.y() * 0.01

        dx = event.position().x() - self.last_mouse_pos.x()
        dy = event.position().y() - self.last_mouse_pos.y()

        self._apply_camera_rotation(dx, dy)
        self.last_mouse_pos = event.position()
        self.update_mvp()
        self.update()

        self._emit_rotation_feedback()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        wheelEvent

        :param event: QWheelEvent
        :return: None
        Sets zoom level
        """
        delta = event.angleDelta().y()
        step = 5  # You can adjust sensitivity
        try:
            new_val = (
                self.zoom_value - step if delta > 0 else self.zoom_value + step
            )  # Negative zoom increases
            log.message(f"zoom level: {new_val}", silent=True)
        except Exception:
            pass

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        mouseReleaseEvent

        :param event: QMouseEvent
        :return: None
        """
        log.parameter("event", event)
        self.last_mouse_pos = None

    def _compute_clicked_position(
        self, x: int, y: int, z: int, viewport: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        _compute_clicked_position

        :param x: int
        :param y: int
        :param z: int
        :param viewport: np.ndarray
        :return: np.ndarray or None
        """

        raise NotImplementedError("Should be implemented in subclass")

    def _get_viewport(self) -> np.ndarray:
        """
        _get_viewport

        :return: np.ndarray: Array containing viewport dimensions.
        Retrieve the current OpenGL viewport dimensions.
        """
        viewport = np.zeros(4, dtype=np.int32)
        gl_get_integerv(GL_VIEWPORT)
        return viewport

    def _apply_camera_rotation(self, dx: float, dy: float) -> None:
        """
        _apply_camera_rotation

        :param dx: float
        :param dy: float
        :return: None
        Apply delta rotation based on mouse movement
        """
        self.camera_parameters.rotation_x_axis += dy * 0.5
        self.camera_parameters.rotation_y_axis += dx * 0.5

    def _emit_rotation_feedback(self):
        pass
