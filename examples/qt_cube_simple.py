"""
Simple Qt Cube Renderer - Minimal Dependencies

This is a simplified version that uses only basic Qt OpenGL widgets
without requiring PySide6. It's designed for systems with limited
Qt installations or when you want a minimal example.

Features:
- Basic Qt OpenGL widget
- Legacy OpenGL rendering
- Simple cube with colors
- Mouse controls
- Minimal dependencies

Requirements:
- PyQt5 or PyQt6 (basic Qt installation)
- PyOpenGL
- NumPy
- PicoGL

Usage:
    python examples/qt_cube_simple.py
"""

import sys
from pathlib import Path
from typing import Optional

import numpy as np

# Try different Qt imports
try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
    from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow,
                                   QVBoxLayout, QWidget)

    QT_VERSION = "PySide6"
except ImportError:
    try:
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtOpenGL import QGLWidget as QOpenGLWidget
        from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow,
                                     QVBoxLayout, QWidget)

        QT_VERSION = "PyQt5"
    except ImportError:
        try:
            from PyQt6.QtCore import Qt, QTimer
            from PyQt6.QtOpenGLWidgets import QOpenGLWidget
            from PyQt6.QtWidgets import (QApplication, QLabel, QMainWindow,
                                         QVBoxLayout, QWidget)

            QT_VERSION = "PyQt6"
        except ImportError:
            print("❌ Error: No Qt installation found")
            print("Please install one of: PySide6, PyQt5, or PyQt6")
            sys.exit(1)

# OpenGL imports
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError as e:
    print("❌ Error: PyOpenGL not available")
    print("Please install PyOpenGL: pip install PyOpenGL PyOpenGL_accelerate")
    sys.exit(1)

from examples.data.cube_data import g_color_buffer_data, g_vertex_buffer_data


class SimpleQtCubeWidget(QOpenGLWidget):
    """
    Simple Qt OpenGL widget for cube rendering

    This is a minimal implementation that works with basic Qt installations
    and provides legacy OpenGL cube rendering.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the cube widget"""
        super().__init__(parent)

        # Cube data
        self.vertices = np.array(g_vertex_buffer_data, dtype=np.float32)
        self.colors = np.array(g_color_buffer_data, dtype=np.float32)

        # Animation and control state
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.zoom = 5.0
        self.auto_rotate = True
        self.rotation_speed = 1.0

        # Mouse state
        self.last_mouse_pos = None

        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS

    def initializeGL(self):
        """Initialize OpenGL state"""
        # Set up OpenGL state
        glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark blue background
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Set up lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

        # Set up material properties
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)

        print(f"✅ Simple Qt Cube Widget initialized (using {QT_VERSION})")

    def resizeGL(self, w: int, h: int):
        """Handle window resize"""
        # Set up projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h, 0.1, 100.0)

        # Return to modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

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
        self.draw_cube()

    def draw_cube(self):
        """Draw the cube using legacy OpenGL immediate mode"""
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        # Set up vertex and colour arrays
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glColorPointer(3, GL_FLOAT, 0, self.colors)

        # Draw the cube
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices) // 3)

        # Clean up
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

    def animate(self):
        """Animation loop - called by timer"""
        if self.auto_rotate:
            self.rotation_y += self.rotation_speed
            if self.rotation_y >= 360.0:
                self.rotation_y -= 360.0
        self.update()

    def mousePressEvent(self, event):
        """Handle mouse press"""
        self.last_mouse_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse movement for manual rotation"""
        if event.buttons() & Qt.LeftButton and self.last_mouse_pos:
            # Manual rotation
            self.auto_rotate = False
            delta = event.pos() - self.last_mouse_pos
            self.rotation_x += delta.y() * 0.5
            self.rotation_y += delta.x() * 0.5

            # Clamp rotation
            self.rotation_x = max(-90, min(90, self.rotation_x))

        self.last_mouse_pos = event.pos()
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
            print("Reset view")
        elif event.key() == Qt.Key_Escape:
            # Close application
            self.parent().close()
        else:
            super().keyPressEvent(event)


class SimpleQtCubeWindow(QMainWindow):
    """
    Simple main window for the Qt cube renderer
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PicoGL Simple Qt Cube - {QT_VERSION}")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Create info label
        info_text = f"""
        <h3>PicoGL Simple Qt Cube Renderer</h3>
        <p><b>Qt Version:</b> {QT_VERSION}</p>
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
        info_label = QLabel(info_text)
        info_label.setMaximumHeight(180)
        layout.addWidget(info_label)

        # Create OpenGL widget
        self.gl_widget = SimpleQtCubeWidget()
        layout.addWidget(self.gl_widget)

        # Set focus to OpenGL widget for keyboard input
        self.gl_widget.setFocusPolicy(Qt.StrongFocus)
        self.gl_widget.setFocus()

    def keyPressEvent(self, event):
        """Handle keyboard input at window level"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def main():
    """Main function to run the simple Qt cube renderer"""
    print("🚀 Starting PicoGL Simple Qt Cube Renderer...")

    # Create and show window
    app = QApplication(sys.argv)
    window = SimpleQtCubeWindow()
    window.show()

    print("✅ Simple Qt Cube Renderer started successfully!")
    print(f"   - Qt Version: {QT_VERSION}")
    print("   - Window: 800x600")
    print("   - Rendering: Legacy OpenGL")
    print("   - Controls: Mouse drag, wheel, keyboard")

    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
