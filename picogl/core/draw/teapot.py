"""
Draw the teapot using built-in GLUT primitives.
"""
import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import glVertex3f

from picogl.backend.gl.api import gl_vertex_3f
from picogl.backend.gl.api.color import gl_color_rgb, gl_color_3f
from picogl.backend.gl.api.enable import toggle_capability, gl_enable, gl_disable
from picogl.backend.gl.api.polygon_mode import gl_polygon_mode
from picogl.backend.gl.capability import GLFixedFunctionCapability, GLMaterialFace
from picogl.backend.gl.enums import GLDrawMode
from picogl.backend.gl.state.fill import GLFillMode
from picogl.backend.gl.state.immediate import gl_immediate_drawing
from picogl.backend.glut import glut_solid_teapot
from picogl.core.rgbcolor import RGBColor


def draw_teapot(wireframe_mode):
    """Draw the teapot using built-in OpenGL primitives."""
    # Set polygon mode
    if wireframe_mode:
        fill_mode = GLFillMode.LINE
        color = RGBColor.RED # Red WireFrame
    else:
        fill_mode = GLFillMode.FILL
        color = RGBColor(0.8, 0.2, 0.2)  # Red teapot
    gl_color_rgb(color)
    toggle_capability(
        enabled=not wireframe_mode,
        capability=GLFixedFunctionCapability.LIGHTING,
    )
    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, fill_mode)
    # Draw the teapot
    glut_solid_teapot(1.0)

    # Reset polygon mode
    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
    gl_enable(GLFixedFunctionCapability.LIGHTING)


def draw_normals():
    """Draw normal vectors (simplified)."""
    gl_disable(GLFixedFunctionCapability.LIGHTING)
    gl_color_3f((0.0, 1.0, 0.0))  # Green normals
    with gl_immediate_drawing(GLDrawMode.LINES):
        # Draw a few normal vectors for demonstration
        for i in range(0, 360, 30):
            angle = i * 3.14159 / 180.0
            x = 0.5 * np.cos(angle)
            y = 0.5 * np.sin(angle)
            z = 0.0

            # Normal vector (simplified)
            nx = x
            ny = y
            nz = z

            gl_vertex_3f(x, y, z)
            glVertex3f(x + nx * 0.2, y + ny * 0.2, z + nz * 0.2)

    gl_enable(GLFixedFunctionCapability.LIGHTING)


def draw_teapot_with_normals(wireframe_mode, show_normals):
    """Draw the teapot using built-in OpenGL primitives."""
    # Set polygon mode
    if wireframe_mode:
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)
        gl_disable(GLFixedFunctionCapability.LIGHTING)
        red_teapot = RGBColor(1.0, 0.0, 0.0)
        gl_color_3f(*red_teapot.tuple)  # Red wireframe
    else:
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
        gl_enable(GLFixedFunctionCapability.LIGHTING)
        gl_color_rgb(RGBColor(0.8, 0.2, 0.2))  # Red teapot

    # Draw the teapot
    glut_solid_teapot(1.0)

    # Draw normals if enabled
    if show_normals and not wireframe_mode:
        draw_normals()

    # Reset polygon mode
    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
    gl_enable(GLFixedFunctionCapability.LIGHTING)