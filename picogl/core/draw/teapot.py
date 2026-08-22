"""
Draw the teapot using built-in GLUT primitives.
"""
import numpy as np

from picogl.backend.gl.api import gl_vertex_3f
from picogl.backend.gl.api.color import gl_color_3f, gl_color_rgb
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.enums import GLDrawMode
from picogl.backend.gl.state.fill import GLFillMode
from picogl.backend.gl.state.immediate import gl_immediate_drawing
from picogl.backend.gl.state.scoped import disabled
from picogl.backend.glut import glut_solid_teapot
from picogl.core.rgbcolor import RGBColor
from picogl.polygon.mode import polygon_mode


def draw_teapot(wireframe_mode):
    """Draw the teapot using built-in OpenGL primitives."""
    if wireframe_mode:
        with disabled(GLFixedFunctionCapability.LIGHTING):
            with polygon_mode(GLFillMode.LINE):
                gl_color_rgb(RGBColor.RED)
                glut_solid_teapot(1.0)
        return

    gl_color_rgb(RGBColor(0.8, 0.2, 0.2))
    glut_solid_teapot(1.0)


def draw_normals():
    """Draw normal vectors (simplified)."""
    with disabled(GLFixedFunctionCapability.LIGHTING):
        gl_color_rgb(RGBColor.GREEN)
        with gl_immediate_drawing(GLDrawMode.LINES):
            for i in range(0, 360, 30):
                angle = i * 3.14159 / 180.0
                x = 0.5 * np.cos(angle)
                y = 0.5 * np.sin(angle)
                z = 0.0

                nx = x
                ny = y
                nz = z

                gl_vertex_3f(x, y, z)
                gl_vertex_3f(x + nx * 0.2, y + ny * 0.2, z + nz * 0.2)


def draw_teapot_with_normals(wireframe_mode, show_normals):
    """Draw the teapot using built-in OpenGL primitives."""
    if wireframe_mode:
        with disabled(GLFixedFunctionCapability.LIGHTING):
            with polygon_mode(GLFillMode.LINE):
                gl_color_3f(*RGBColor.RED.tuple)
                glut_solid_teapot(1.0)
        return

    gl_color_rgb(RGBColor(0.8, 0.2, 0.2))
    glut_solid_teapot(1.0)

    if show_normals:
        draw_normals()
