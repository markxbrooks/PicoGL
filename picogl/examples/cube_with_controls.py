import sys
from typing import Any

import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from backend.gl.api.legacy.matrix import gl_pushed_matrix
from picogl.backend.gl.api.clear import gl_clear, gl_clear_color
from picogl.backend.gl.api.enable import gl_enable
from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.enums.legacy.scale import (
    gl_pop_matrix,
    gl_push_matrix,
    gl_rotatef,
    gl_scalef,
    gl_translatef,
    gl_viewport,
)
from picogl.backend.legacy.core.pipeline import LegacyPipeline
from picogl.renderer import MeshData
from picogl.renderer.legacy_glmesh import LegacyGLMesh


def _triangulate_quads(quad_indices: list[int]) -> np.ndarray:
    """Convert quad face indices to triangle indices for LegacyGLMesh."""
    triangles: list[int] = []
    for i in range(0, len(quad_indices), 4):
        a, b, c, d = quad_indices[i : i + 4]
        triangles.extend([a, b, c, c, d, a])
    return np.array(triangles, dtype=np.uint32)


def _multiply_by_pi(val) -> float | Any:
    return np.pi * val


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        self.rot_x = None
        self.rot_y = None
        self.rot_z = None
        self.zoom = None
        self.parent = parent
        self.cube_mesh: LegacyGLMesh | None = None
        QOpenGLWidget.__init__(self, parent)
        self.pdb_data = None

    def load_pdb_data(self, pdb_data):
        self.pdb_data = pdb_data
        self.update()

    def initializeGL(self):
        gl_clear_color((0.0, 0.0, 0.0, 1.0))
        gl_enable(GLPipelineCapability.DEPTH_TEST)
        self.init_geometry()
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0
        self.zoom = -50.0

    def resizeGL(self, width, height):
        gl_viewport(0, 0, width, height)
        LegacyPipeline.set_projection(45.0, width / float(height), 1.0, 100.0)

    def paintGL(self):
        gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
        with gl_pushed_matrix():
            gl_translatef(0.0, 0.0, float(self.zoom))
            gl_scalef(20.0, 20.0, 20.0)
            gl_rotatef(float(self.rot_x), 1.0, 0.0, 0.0)
            gl_rotatef(float(self.rot_y), 0.0, 1.0, 0.0)
            gl_rotatef(float(self.rot_z), 0.0, 0.0, 1.0)
            gl_translatef(-0.5, -0.5, -0.5)

            if self.cube_mesh is not None:
                with self.cube_mesh:
                    self.cube_mesh.draw()

    def init_geometry(self):
        """init geometry"""
        cube_vertices = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [1.0, 0.0, 1.0],
                [1.0, 1.0, 1.0],
                [0.0, 1.0, 1.0],
            ],
            dtype=np.float32,
        )
        cube_colors = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [1.0, 0.0, 1.0],
                [1.0, 1.0, 1.0],
                [0.0, 1.0, 1.0],
            ],
            dtype=np.float32,
        )
        quad_indices = [
            0,
            1,
            2,
            3,
            3,
            2,
            6,
            7,
            1,
            0,
            4,
            5,
            2,
            1,
            5,
            6,
            0,
            3,
            7,
            4,
            7,
            6,
            5,
            4,
        ]
        mesh_data = MeshData.from_raw(
            vertices=cube_vertices,
            colors=cube_colors,
            indices=_triangulate_quads(quad_indices),
        )
        self.cube_mesh = LegacyGLMesh.from_mesh_data(mesh_data)

    def set_rot_x(self, val):
        self.rot_x = _multiply_by_pi(val)

    def set_rot_y(self, val):
        self.rot_y = _multiply_by_pi(val)

    def set_rot_z(self, val):
        self.rot_z = _multiply_by_pi(val)

    def set_zoom(self, val):
        self.zoom = val
        self.update()


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.resize(300, 300)
        self.setWindowTitle("Cube OpenGL App")

        self.gl_widget = GLWidget(self)
        self.init_gui()

        timer = QTimer(self)
        timer.setInterval(20)
        timer.timeout.connect(self.gl_widget.update)
        timer.start()

    def init_gui(self):
        central_widget = QWidget()
        xslider_layout = QHBoxLayout()

        gui_layout = QVBoxLayout()
        central_widget.setLayout(gui_layout)

        self.setCentralWidget(central_widget)

        xslider_layout.addWidget(self.gl_widget)

        slider_zoom = QSlider(Qt.Vertical)
        slider_zoom.setMaximum(-20)
        slider_zoom.setMinimum(-80)
        slider_zoom.valueChanged.connect(lambda val: self.gl_widget.set_zoom(val))
        xslider_layout.addWidget(slider_zoom)

        slider_x = QSlider(Qt.Vertical)
        slider_x.valueChanged.connect(lambda val: self.gl_widget.set_rot_x(val))
        xslider_layout.addWidget(slider_x)

        slider_y = QSlider(Qt.Horizontal)
        slider_y.valueChanged.connect(lambda val: self.gl_widget.set_rot_y(val))

        slider_z = QSlider(Qt.Horizontal)
        slider_z.valueChanged.connect(lambda val: self.gl_widget.set_rot_z(val))

        gui_layout.addLayout(xslider_layout)
        gui_layout.addWidget(slider_y)
        gui_layout.addWidget(slider_z)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())
