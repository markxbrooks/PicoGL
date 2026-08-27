"""
Qt-based Cube Renderer using PicoGL's GLBase

This example demonstrates how to create a simple cube renderer using Qt's QOpenGLWidget
through PicoGL's GLBase class. It's designed for legacy displays and systems that
prefer Qt over GLUT.

Features:
- Legacy OpenGL rendering (compatible with older systems)
- Mouse controls for rotation and zoom
- Colorful cube with vertex colors
- Qt-based window management
- Cross-platform compatibility

Requirements:
- PySide6 (Qt6)
- PyOpenGL
- NumPy
- PicoGL

Usage:
    python examples/qt_cube.py
"""

import sys
from typing import Optional

from picogl.backend.gl.mode import GLMode
from picogl.ui.backend.qt.base import GLBase
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget


class LegacyQtObjectWindow(QMainWindow):
    """
    Main window for the Qt Object renderer
    """

    def __init__(self, parent, gl_mode: GLMode = GLMode.LEGACY):
        super().__init__()
        self.parent = parent
        self.gl_mode = gl_mode
        self.layout: Optional[QVBoxLayout] = None
        self.gl_widget: Optional[GLBase] = None
        self.setWindowTitle("PicoGL Qt Object Renderer - Legacy OpenGL")
        self.setGeometry(100, 100, 800, 600)
        self.object_file_path = None
        self.ui_init()

    def ui_init(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Create layout
        self.layout = QVBoxLayout(central_widget)
        # Create info label
        self.set_layout(self.layout)

    def set_layout(self, layout):
        raise NotImplementedError("To be implemented in subclass")

    def toggle_auto_rotate(self):
        """Toggle auto-rotation"""
        self.gl_widget.auto_rotate = not self.gl_widget.auto_rotate
        print(f"Auto-rotation: {'ON' if self.gl_widget.auto_rotate else 'OFF'}")

    def reset_view(self):
        """Reset the view"""
        self.gl_widget.rotation_x = 0.0
        self.gl_widget.rotation_y = 0.0
        self.gl_widget.zoom = 5.0
        self.gl_widget.mvp_parameters.x = 0.0
        self.gl_widget.mvp_parameters.y = 0.0
        self.gl_widget.mvp_parameters.pan_x = 0.0
        self.gl_widget.mvp_parameters.pan_y = 0.0
        self.gl_widget.camera_parameters.rotation_x_axis = 0.0
        self.gl_widget.camera_parameters.rotation_y_axis = 0.0
        self.gl_widget.camera_parameters.rotation_z_axis = 0.0
        self.gl_widget.camera_parameters.translation_x_axis = 0.0
        self.gl_widget.camera_parameters.translation_y_axis = 0.0
        self.gl_widget.camera_parameters.translation_zoom = 0.0
        print("View reset")

    def keyPressEvent(self, event):
        """Handle keyboard input at window level"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
