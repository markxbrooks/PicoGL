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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from picogl.ui.backend.qt.legacy.renderer import LegacyQtObjectRenderer
from picogl.ui.backend.qt.legacy.window import LegacyQtObjectWindow

# OpenGL imports
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError as e:
    print("❌ Error: PyOpenGL not available")
    print("Please install PyOpenGL: pip install PyOpenGL PyOpenGL_accelerate")
    sys.exit(1)


class QtCubeWindow(LegacyQtObjectWindow):
    """
    Main window for the Qt Object renderer
    """

    def __init__(self):
        super().__init__(parent=self)
        self.layout: Optional[QVBoxLayout] = None
        self.gl_widget: Optional[LegacyQtObjectRenderer] = None
        self.setWindowTitle("PicoGL Qt Object Renderer - Legacy OpenGL")
        self.setGeometry(100, 100, 800, 600)
        self.ui_init()

    def ui_init(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Create layout
        self.setup_layout(central_widget)

    def setup_layout(self, central_widget):
        self.layout = QVBoxLayout(central_widget)
        # Create info label
        self.set_layout(self.layout)

    def set_layout(self, layout):
        info_label = QLabel()
        info_label.setText("""
            <h3>PicoGL Qt Cube Renderer</h3>
            <p><b>Controls:</b></p>
            <ul>
            <li><b>Mouse Drag:</b> Manual rotation (disables auto-rotation)</li>
            <li><b>Mouse Wheel:</b> Zoom in/out</li>
            <li><b>Space:</b> Toggle auto-rotation</li>
            <li><b>R:</b> Reset view</li>
            <li><b>Escape:</b> Close application</li>
            </ul>
            <p><b>Rendering:</b> Legacy OpenGL (compatible with older systems)</p>
            """
                           )
        info_label.setMaximumHeight(150)
        layout.addWidget(info_label)
        # Create OpenGL widget
        self.gl_widget = LegacyQtObjectRenderer()
        layout.addWidget(self.gl_widget)
        # Create control buttons
        button_layout = QVBoxLayout()
        auto_rotate_btn = QPushButton("Toggle Auto-Rotation")
        auto_rotate_btn.clicked.connect(self.toggle_auto_rotate)
        button_layout.addWidget(auto_rotate_btn)
        reset_btn = QPushButton("Reset View")
        reset_btn.clicked.connect(self.reset_view)
        button_layout.addWidget(reset_btn)
        layout.addLayout(button_layout)
        # Set focus to OpenGL widget for keyboard input
        self.gl_widget.setFocusPolicy(Qt.StrongFocus)
        self.gl_widget.setFocus()


def main():
    """Main function to run the Qt cube renderer"""
    print("🚀 Starting PicoGL Qt Cube Renderer...")

    # Check for Qt availability
    try:
        app = QApplication(sys.argv)
    except ImportError as e:
        print("❌ Error: PySide6 not available")
        print("Please install PySide6: pip install PySide6")
        return 1

    # Create and show window
    window = QtCubeWindow()
    window.show()

    print("✅ Qt Cube Renderer started successfully!")
    print("   - Window: 800x600")
    print("   - Rendering: Legacy OpenGL")
    print("   - Controls: Mouse drag, wheel, keyboard")

    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
