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
    python examples/legacy_qt_cube.py
"""

from typing import Optional

from picogl.backend.gl.mode import GLMode
from picogl.ui.backend.qt.base import GLBase
from picoui.dimensions import Dimensions, Point, WindowGeometry
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget


class LegacyQtObjectWindow(QMainWindow):
    """
    Main window for the Qt Object renderer
    """

    window_geometry = WindowGeometry(
        position=Point(x=100, y=100),
        dimensions=Dimensions(width=800, height=600),
    )

    def __init__(self, parent, gl_mode: GLMode = GLMode.LEGACY):
        super().__init__()
        self.parent = parent
        self.gl_mode = gl_mode
        self.layout: Optional[QVBoxLayout] = None
        self.gl_widget: Optional[GLBase] = None
        self.setWindowTitle("PicoGL Qt Object Renderer - Legacy OpenGL")
        self.setGeometry(*self.window_geometry.to_tuple())
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
        self.initialize_gl_widget()
        self.initialize_mvp()
        self.initialize_camera()
        print("View reset")

    def initialize_gl_widget(self):
        self.gl_widget.initialize()

    def initialize_camera(self):
        self.gl_widget.camera_parameters.initialize()

    def initialize_mvp(self):
        self.gl_widget.mvp_parameters.initialize()

    def keyPressEvent(self, event):
        """Handle keyboard input at window level"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
