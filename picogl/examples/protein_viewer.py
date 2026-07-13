import os.path
import sys  # we'll need this later to run our Qt application
from pathlib import Path

import numpy as np
import OpenGL.GL as gl  # python wrapping of OpenGL
from molib.ligand.pdb.layouts.hetatm import HETATMLayout
from OpenGL import GLU  # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.GL import (
    GL_FLOAT,
    GL_STATIC_DRAW,
    glBindBuffer,
    glBufferData,
    glGenBuffers,
    glScale,
)
from OpenGL.GLU import gluLookAt
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

from picogl.backend.gl.api.clear import gl_clear_color
from picogl.backend.gl.api.enable import gl_enable
from picogl.backend.gl.enums import GLBufferTarget, GLDrawMode
from picogl.backend.gl.enums.legacy.scale import gl_viewport
from picogl.backend.gl.state.client import GLClientState
from picogl.backend.legacy.core.vertex.buffer.client_states import legacy_client_states


def _pdb_atom_xyz(line: str) -> list[float]:
    """Parse x/y/z from an ATOM or HETATM line (shared PDB column layout)."""
    return [
        HETATMLayout.x.parse(line),
        HETATMLayout.y.parse(line),
        HETATMLayout.z.parse(line),
    ]


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        self.rot_x = None
        self.rot_y = None
        self.rot_z = None
        self.zoom = None
        self.parent = parent
        QOpenGLWidget.__init__(self, parent)
        self.pdb_data = None  # This will hold your PDB data

    def load_pdb_data(self, pdb_data):
        self.pdb_data = pdb_data
        self.update()  # Trigger a repaint

    def initializeGL(self):
        gl_clear_color((0.15, 0.15, 0.2, 1.0))
        gl_enable(gl.GL_DEPTH_TEST)

        self.init_geometry()

        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0
        self.zoom = -50.0

    def resizeGL(self, width, height):
        gl_viewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def pdb_file_parse_atoms(self, file_path):
        coordinates = []
        with open(file_path, "r") as file:
            for line in file:
                if HETATMLayout.record_type.parse(line) == "ATOM":
                    coordinates.append(_pdb_atom_xyz(line))
        return np.array(coordinates, dtype=np.float32)

    def pdb_file_parse_calphas(self, file_path):
        coordinates = []
        with open(file_path, "r") as file:
            for line in file:
                if HETATMLayout.record_type.parse(line) != "ATOM":
                    continue
                if HETATMLayout.atom_name.parse(line) != "CA":
                    continue
                coordinates.append(_pdb_atom_xyz(line))
        return np.array(coordinates, dtype=np.float32)

    def center_coordinates(self, coordinates):
        center = np.mean(coordinates, axis=0)
        return coordinates - center

    # Create a VBO object
    def create_vbo_object(self, coordinates):
        vbo = glGenBuffers(1)
        glBindBuffer(GLBufferTarget.ARRAY, vbo)
        glBufferData(
            GLBufferTarget.ARRAY, coordinates.nbytes, coordinates, GL_STATIC_DRAW
        )
        return vbo

    def init_geometry(self):
        pdb_path = os.path.join(Path.home(), "Downloads", "6VFF.pdb")
        if os.path.isfile(pdb_path):
            self.coordinates = self.pdb_file_parse_calphas(pdb_path)
        else:
            # Fallback helix when the demo PDB is not on disk.
            t = np.linspace(0, 4 * np.pi, 200, dtype=np.float32)
            self.coordinates = np.column_stack(
                (10 * np.cos(t), 10 * np.sin(t), t * 3)
            ).astype(np.float32)

        if len(self.coordinates) == 0:
            self.centered_coordinates = self.coordinates
            self.vbo = None
            return

        self.centered_coordinates = self.center_coordinates(self.coordinates)
        self.vbo = self.create_vbo_object(self.centered_coordinates)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gluLookAt(0, 0, -40, 0, 0, 0, 0, 1, 0)

        gl.glPushMatrix()
        gl.glTranslate(0.0, 0.0, self.zoom)
        glScale(0.1, 0.1, 0.1)
        gl.glRotate(self.rot_x, 1.0, 0.0, 0.0)
        gl.glRotate(self.rot_y, 0.0, 1.0, 0.0)
        gl.glRotate(self.rot_z, 0.0, 0.0, 1.0)

        if self.vbo is None or len(self.coordinates) < 2:
            gl.glPopMatrix()
            return

        gl.glLineWidth(2.0)
        glBindBuffer(GLBufferTarget.ARRAY, self.vbo)
        with legacy_client_states(GLClientState.VERTEX):
            gl.glVertexPointer(3, GL_FLOAT, 0, None)
            gl.glDrawArrays(int(GLDrawMode.LINE_STRIP), 0, len(self.coordinates))
        gl.glPopMatrix()

    def set_rot_x(self, val):
        self.rot_x = np.pi * val

    def set_rot_y(self, val):
        self.rot_y = np.pi * val

    def set_rot_z(self, val):
        self.rot_z = np.pi * val

    def set_zoom(self, val):
        self.zoom = val


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)  # call the init for the parent class

        self.resize(300, 300)
        self.setWindowTitle("Cube OpenGL App")

        self.gl_widget = GLWidget(self)
        self.init_gui()

        timer = QTimer(self)
        timer.setInterval(20)  # period, in milliseconds
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
        slider_zoom.setMaximum(-20.0)
        slider_zoom.setMinimum(-80.0)
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
