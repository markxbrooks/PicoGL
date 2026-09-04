"""
A module to create and display a simple OpenGL-based graphics application with slider controls for rotations and zoom.

This module contains the GLSliderWindow class, which provides a windowed application
that integrates OpenGL rendering with slider-based controls for modifying the zoom
level and rotation angles of a displayed 3D object. It uses the PySide6 framework
for building the GUI.

Classes:
    GLSliderWindow: A QMainWindow subclass that hosts an OpenGL widget and
    controls for interacting with the 3D cube.
"""

# from examples.cube_with_controls import GLCubeWidget
# rom examples.protein_viewer import GLProteinWidget

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QHBoxLayout, QMainWindow, QSlider, QVBoxLayout,
                               QWidget)


class GLSliderWindow(QMainWindow):

    def __init__(self, widget: "GLCubeWidget | GLProteinWidget"):
        QMainWindow.__init__(self)  # call the init for the parent class

        self.resize(600, 600)
        self.setWindowTitle("OpenGL App")

        self.gl_widget = widget
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
