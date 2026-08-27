"""
LegacyQtObjectRenderer
"""

from typing import Optional

import numpy as np
from decologr import Decologr as log
from picogl.backend.gl.api.clear import gl_clear_color
from picogl.backend.gl.api.color import gl_color_material
from picogl.backend.gl.api.enable import gl_enable, gl_enable_capability_list
from picogl.backend.gl.api.legacy.matrix import gl_matrix_mode_context
from picogl.backend.gl.api.matrix import gl_matrix_mode
from picogl.backend.gl.api.rotate import gl_rotate_f
from picogl.backend.gl.capability import (
    GLFixedFunctionCapability,
    GLMaterialFace,
    GLPipelineCapability,
)
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import gl_load_identity
from picogl.backend.gl.legacy.lighting import (
    DEFAULT_LEGACY_MATERIAL,
    gl_legacy_lighting,
)
from picogl.backend.gl.mode import GLMode
from picogl.backend.gl.state.fill import GLCapability, GLColorMaterialMode
from picogl.core.setup.camera import gl_setup_camera
from picogl.core.setup.view import gl_setup_view
from picogl.examples import g_color_buffer_data, g_vertex_buffer_data
from picogl.renderer import MeshData
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.ui.backend.qt.base import GLBase
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget


class LegacyQtObjectRenderer(GLBase):
    """
    Qt-based cube renderer using legacy OpenGL

    This class extends GLBase to provide a simple cube renderer with
    mouse controls for rotation and zoom.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the cube renderer"""
        super().__init__(parent, gl_mode=GLMode.LEGACY)

        # Cube data
        self._initialized: bool = False
        self.gl_mesh_data = None
        self.mesh_data: Optional[MeshData] = None
        self.vertices = np.array(g_vertex_buffer_data, dtype=np.float32)
        self.colors = np.array(g_color_buffer_data, dtype=np.float32)

        # Generate indices for the cube (36 vertices = 12 triangles)
        self.indices = np.arange(36, dtype=np.uint32)

        # Animation and control state
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.zoom = 5.0
        self.auto_rotate = True
        self.rotation_speed = 1.0

        # Initialize mvp_parameters to avoid None values
        self.mvp_parameters.x = 0.0
        self.mvp_parameters.y = 0.0
        self.mvp_parameters.pan_x = 0.0
        self.mvp_parameters.pan_y = 0.0

        # Initialize camera_parameters to avoid None values
        self.camera_parameters.rotation_x_axis = 0.0
        self.camera_parameters.rotation_y_axis = 0.0
        self.camera_parameters.rotation_z_axis = 0.0
        self.camera_parameters.translation_x_axis = 0.0
        self.camera_parameters.translation_y_axis = 0.0
        self.camera_parameters.translation_zoom = 0.0

        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS

    def initializeGL(self):
        """Initialize OpenGL state for cube rendering"""
        super().initializeGL()
        self.initialize_state()
        self.initialize_lighting()
        # Create and upload mesh data
        self.initialize()

    def initialize(self):
        if self._initialized:
            return
        self.mesh_data = MeshData.from_raw(
            vertices=self.vertices, colors=self.colors, indices=self.indices
        )
        self.gl_mesh_data = LegacyGLMesh.from_mesh_data(mesh=self.mesh_data)
        # self.gl_mesh_data.upload()
        self._initialized = True
        log.message("✅ Qt Cube Renderer initialized")

    def initialize_state(self):
        # Set up OpenGL state
        gl_clear_color(0.1, 0.1, 0.2, 1.0)  # Dark blue background
        gl_enable(GLPipelineCapability.DEPTH_TEST)

    def initialize_materials(self):
        """Apply the default legacy Phong material."""
        DEFAULT_LEGACY_MATERIAL.apply(GLMaterialFace.FRONT_AND_BACK)

    def initialize_lighting(self):
        gl_enable_capability_list(
            [
                GLFixedFunctionCapability.LIGHTING,
                GLFixedFunctionCapability.LIGHT0,
                GLCapability.COLOR_MATERIAL,
            ]
        )
        gl_color_material(
            GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE
        )
        gl_legacy_lighting()

    def resizeGL(self, w: int, h: int):
        """Handle window resize"""
        super().resizeGL(w, h)

    def _emit_rotation_feedback(self):
        pass

    def paintGL(self):
        """Render the cube scene"""
        # Clear buffers
        gl_setup_view()

        # Set up modelview matrix
        with gl_matrix_mode_context():
            # Position camera
            gl_setup_camera(Self.zoom)

            # Apply rotations
            gl_rotate_f(self.rotation_x, 1, 0, 0)
            gl_rotate_f(self.rotation_y, 0, 1, 0)

            # Draw the cube using legacy OpenGL
            self.draw()

    def draw(self):
        """Draw the cube using LegacyGLMesh"""
        # Draw using LegacyGLMesh (already created and uploaded in initializeGL)
        if self.gl_mesh_data is not None:
            self.gl_mesh_data.draw()

    def animate(self):
        """Animation loop - called by timer"""
        if self.auto_rotate:
            self.rotation_y += self.rotation_speed
            if self.rotation_y >= 360.0:
                self.rotation_y -= 360.0
        self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse movement for manual rotation"""
        if event.buttons() & Qt.LeftButton:
            # Manual rotation
            self.auto_rotate = False
            delta = event.position() - self.last_mouse_pos
            self.rotation_x += delta.y() * 0.5
            self.rotation_y += delta.x() * 0.5

            # Clamp rotation
            self.rotation_x = max(-90, min(90, self.rotation_x))

            # Update mvp_parameters for compatibility
            self.mvp_parameters.x = self.rotation_x
            self.mvp_parameters.y = self.rotation_y

        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y()
        zoom_factor = 0.1

        if delta > 0:
            self.zoom = max(1.0, self.zoom - zoom_factor)
        else:
            self.zoom = min(20.0, self.zoom + zoom_factor)

        print(f"Zoom: {self.zoom:.1f}")
        super().wheelEvent(event)

    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if event.key() == Qt.Key_Space:
            # Toggle auto-rotation
            self.auto_rotate = not self.auto_rotate
            print(f"Auto-rotation: {'ON' if self.auto_rotate else 'OFF'}")
        elif event.key() == Qt.Key_R:
            # Reset rotation
            self.rotation_x = 0.0
            self.rotation_y = 0.0
            self.zoom = 5.0
            self.mvp_parameters.x = 0.0
            self.mvp_parameters.y = 0.0
            self.mvp_parameters.pan_x = 0.0
            self.mvp_parameters.pan_y = 0.0
            self.camera_parameters.rotation_x_axis = 0.0
            self.camera_parameters.rotation_y_axis = 0.0
            self.camera_parameters.rotation_z_axis = 0.0
            self.camera_parameters.translation_x_axis = 0.0
            self.camera_parameters.translation_y_axis = 0.0
            self.camera_parameters.translation_zoom = 0.0
            print("Reset view")
        elif event.key() == Qt.Key_Escape:
            # Close application
            self.parent().close()
        else:
            super().keyPressEvent(event)
