"""
Simple Qt Cube Renderer - Minimal Dependencies

A minimal Qt OpenGL cube example routed through PicoGL's legacy backend,
mesh types, and state helpers instead of raw client-state draw calls.

Features:
- Basic Qt OpenGL widget (PySide6 / PyQt5 / PyQt6)
- PicoGL GLBackend + LegacyGLMesh rendering
- Mouse controls and auto-rotation
- Minimal dependencies beyond Qt, PyOpenGL, NumPy, and PicoGL

Usage:
    python examples/qt_cube_simple.py
"""

import sys
from typing import Any, Optional

import numpy as np
from numpy import dtype, generic, ndarray
from picogl.backend.gl.light import GLLightSource

# Try different Qt imports
try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QVBoxLayout,
        QWidget,
    )

    QT_VERSION = "PySide6"
except ImportError:
    try:
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtOpenGL import QGLWidget as QOpenGLWidget
        from PyQt5.QtWidgets import (
            QApplication,
            QLabel,
            QMainWindow,
            QVBoxLayout,
            QWidget,
        )

        QT_VERSION = "PyQt5"
    except ImportError:
        try:
            from PyQt6.QtCore import Qt, QTimer
            from PyQt6.QtOpenGLWidgets import QOpenGLWidget
            from PyQt6.QtWidgets import (
                QApplication,
                QLabel,
                QMainWindow,
                QVBoxLayout,
                QWidget,
            )

            QT_VERSION = "PyQt6"
        except ImportError:
            print("Error: No Qt installation found")
            print("Please install one of: PySide6, PyQt5, or PyQt6")
            sys.exit(1)

try:
    from OpenGL.GL import glGetError, glRotatef
    from OpenGL.raw.GLU import gluLookAt
except ImportError:
    print("Error: PyOpenGL not available")
    print("Please install PyOpenGL: pip install PyOpenGL PyOpenGL_accelerate")
    sys.exit(1)

from picogl.examples.data.cube_data import g_color_buffer_data, g_vertex_buffer_data
from picogl.backend.geometry.factory import LegacyBinding
from picogl.backend.gl.backend import GLBackend
from picogl.backend.gl.capability import (
    GLFixedFunctionCapability,
    GLMaterialFace,
    PhongMaterial,
)
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.state.fill import (
    GLCapability,
    GLColorMaterialMode,
    GLFace,
    GLLight,
    GLLightParameter,
)
from picogl.renderer.legacy_glmesh import LegacyGLMesh


def _to_np_array(data) -> ndarray[Any, dtype[Any]] | ndarray[Any, dtype[generic]]:
    return np.array(data, dtype=np.float32)


class SimpleQtCubeWidget(QOpenGLWidget):
    """Minimal Qt cube widget using PicoGL legacy mesh + backend drivers."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.backend = GLBackend(LegacyBinding())
        self.gl_mesh: Optional[LegacyGLMesh] = None
        self._gl_ready = False

        self.vertices = _to_np_array(data=g_vertex_buffer_data)
        self.colors = _to_np_array(data=g_color_buffer_data)
        self.indices = np.arange(len(self.vertices) // 3, dtype=np.uint32)

        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.zoom = 5.0
        self.auto_rotate = True
        self.rotation_speed = 1.0

        self.last_mouse_pos = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def initializeGL(self):
        """Initialize OpenGL through PicoGL backend helpers."""
        self.backend.frame.set_clear_color((0.1, 0.1, 0.2, 1.0))
        self.backend.depth.set_depth_test(True)
        self.backend.depth.set_depth_func_gl_less()

        self.backend.capabilities.enable(GLFixedFunctionCapability.LIGHTING)
        self.backend.capabilities.enable(GLFixedFunctionCapability.LIGHT0)
        self.backend.capabilities.enable(GLCapability.COLOR_MATERIAL)
        self.backend.legacy.set_color_material(
            GLFace.FRONT_AND_BACK,
            GLColorMaterialMode.AMBIENT_AND_DIFFUSE,
        )
        self.backend.legacy.set_light(
            [1.0, 1.0, 1.0, 0.0],
            light=GLLight.LIGHT0,
        )

        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.AMBIENT,
            [0.3, 0.3, 0.3, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.DIFFUSE,
            [0.8, 0.8, 0.8, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.SPECULAR,
            [1.0, 1.0, 1.0, 1.0],
        )

        material = PhongMaterial(
            ambient=(0.2, 0.2, 0.2, 1.0),
            diffuse=(0.8, 0.8, 0.8, 1.0),
            specular=(1.0, 1.0, 1.0, 1.0),
            shininess=50.0,
        )
        self.backend.legacy.set_material(GLMaterialFace.FRONT_AND_BACK, material)

        verts = self.vertices.reshape(-1, 3)
        cols = self.colors.reshape(-1, 3)
        self.gl_mesh = LegacyGLMesh(
            vertices=verts,
            faces=self.indices,
            colors=cols,
        )
        self.gl_mesh.upload()
        self._gl_ready = True

        print(f"Simple Qt Cube Widget initialized (using {QT_VERSION}, PicoGL API)")

    def resizeGL(self, w: int, h: int):
        """Resize viewport and projection via PicoGL drivers."""
        h = max(h, 1)
        self.backend.frame.viewport(0, 0, w, h)
        aspect = float(w) / float(h)
        self.backend.legacy.set_matrix_mode_projection()
        self.backend.legacy.load_identity()
        self.backend.legacy.set_perspective(45.0, aspect, 0.1, 100.0)
        self.backend.legacy.set_matrix_mode_model_view()
        self.backend.legacy.load_identity()

    def _set_modelview(self) -> None:
        """Match legacy Qt cube camera: eye on +Z axis, then orbit rotations."""
        self.backend.legacy.set_matrix_mode_model_view()
        self.backend.legacy.load_identity()
        gluLookAt(0.0, 0.0, float(self.zoom), 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        glRotatef(float(self.rotation_x), 1.0, 0.0, 0.0)
        glRotatef(float(self.rotation_y), 0.0, 1.0, 0.0)

    def paintGL(self):
        """Render the cube through PicoGL frame clear + legacy mesh draw."""
        if not self._gl_ready or self.gl_mesh is None:
            return

        self.backend.frame.clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
        self._set_modelview()
        self.gl_mesh.draw()

        err = glGetError()
        if err:
            print(f"OpenGL error after draw: {err}")

    def animate(self):
        if self.auto_rotate:
            self.rotation_y += self.rotation_speed
            if self.rotation_y >= 360.0:
                self.rotation_y -= 360.0
        self.update()

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.last_mouse_pos is not None:
            self.auto_rotate = False
            delta = event.pos() - self.last_mouse_pos
            self.rotation_x += delta.y() * 0.5
            self.rotation_y += delta.x() * 0.5
            self.rotation_x = max(-90, min(90, self.rotation_x))

        self.last_mouse_pos = event.pos()
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        zoom_factor = 0.1
        if delta > 0:
            self.zoom = max(1.0, self.zoom - zoom_factor)
        else:
            self.zoom = min(20.0, self.zoom + zoom_factor)
        print(f"Zoom: {self.zoom:.1f}")
        super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.auto_rotate = not self.auto_rotate
            print(f"Auto-rotation: {'ON' if self.auto_rotate else 'OFF'}")
        elif event.key() == Qt.Key_R:
            self.rotation_x = 0.0
            self.rotation_y = 0.0
            self.zoom = 5.0
            print("Reset view")
        elif event.key() == Qt.Key_Escape:
            self.parent().close()
        else:
            super().keyPressEvent(event)


class SimpleQtCubeWindow(QMainWindow):
    """Main window hosting the simple PicoGL cube widget."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PicoGL Simple Qt Cube - {QT_VERSION}")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

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
        <p><b>Rendering:</b> PicoGL GLBackend + LegacyGLMesh (legacy OpenGL)</p>
        """
        info_label = QLabel(info_text)
        info_label.setMaximumHeight(180)
        layout.addWidget(info_label)

        self.gl_widget = SimpleQtCubeWidget()
        layout.addWidget(self.gl_widget)

        self.gl_widget.setFocusPolicy(Qt.StrongFocus)
        self.gl_widget.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def main():
    print("Starting PicoGL Simple Qt Cube Renderer...")
    app = QApplication(sys.argv)
    window = SimpleQtCubeWindow()
    window.show()
    print("Simple Qt Cube Renderer started successfully!")
    print(f"   - Qt Version: {QT_VERSION}")
    print("   - Window: 800x600")
    print("   - Rendering: PicoGL legacy backend + LegacyGLMesh")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

"""test"""
