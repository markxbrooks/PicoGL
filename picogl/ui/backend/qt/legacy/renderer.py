from typing import Optional

import numpy as np
from OpenGL.GL import glMaterialfv, glLightfv
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_FRONT_AND_BACK, GL_AMBIENT, GL_DIFFUSE, GL_SPECULAR, glMaterialf, \
    GL_SHININESS, glClearColor, glEnable, GL_DEPTH_TEST, GL_LIGHTING, GL_LIGHT0, GL_COLOR_MATERIAL, glColorMaterial, \
    GL_AMBIENT_AND_DIFFUSE, GL_POSITION, glMatrixMode, GL_PROJECTION, glLoadIdentity, GL_MODELVIEW, glClear, \
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glRotatef
from OpenGL.raw.GLU import gluPerspective, gluLookAt
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget

from examples import g_vertex_buffer_data, g_color_buffer_data
from decologr import Decologr as log
from picogl.renderer import MeshData
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.ui.backend.qt.base import GLBase


class LegacyQtObjectRenderer(GLBase):
    """
    Qt-based cube renderer using legacy OpenGL

    This class extends GLBase to provide a simple cube renderer with
    mouse controls for rotation and zoom.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the cube renderer"""
        super().__init__(parent, gl_mode=True)

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
        self.mvp_parameters.rotation_x = 0.0
        self.mvp_parameters.rotation_y = 0.0
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
        self.initialize_materials()
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

    def initialize_materials(self):
        # Set up material properties
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)

    def initialize_state(self):
        # Set up OpenGL state
        glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark blue background
        glEnable(GL_DEPTH_TEST)

    def initialize_lighting(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        # Set up lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    def resizeGL(self, w: int, h: int):
        """Handle window resize"""
        super().resizeGL(w, h)

        # Set up projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h, 0.1, 100.0)

        # Return to modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def _emit_rotation_feedback(self):
        pass

    def paintGL(self):
        """Render the cube scene"""
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set up modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Position camera
        gluLookAt(0, 0, self.zoom, 0, 0, 0, 0, 1, 0)

        # Apply rotations
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)

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
            self.mvp_parameters.rotation_x = self.rotation_x
            self.mvp_parameters.rotation_y = self.rotation_y

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
            self.mvp_parameters.rotation_x = 0.0
            self.mvp_parameters.rotation_y = 0.0
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
