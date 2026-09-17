"""
Draw the teapot using built-in GLUT primitives.
"""
from typing import Any

import numpy as np
from molib.pdb.coordinate.coordinate import Coordinates
from picogl.backend.gl.api.color import gl_color_rgb
from picogl.backend.gl.api.vertex.vertex_3f import gl_vertex_line
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.enums import GLDrawMode
from picogl.backend.gl.state.fill import GLFillMode
from picogl.backend.gl.state.immediate import gl_immediate_drawing
from picogl.backend.gl.state.scoped import gl_disabled
from picogl.backend.glut import glut_solid_teapot
from picogl.core.rgbcolor import RGBColor
from picogl.polygon.mode import gl_polygon_mode_context

NORMAL_SAMPLE_COUNT = 12
NORMAL_RADIUS = 0.5
NORMAL_LENGTH = 0.2

def draw_teapot(wireframe_mode):
    """Draw the teapot using built-in OpenGL primitives."""
    if wireframe_mode:
        with gl_disabled(GLFixedFunctionCapability.LIGHTING):
            with gl_polygon_mode_context(GLFillMode.LINE):
                gl_color_rgb(RGBColor.RED)
                glut_solid_teapot(1.0)
        return

    gl_color_rgb(RGBColor(0.8, 0.2, 0.2))
    glut_solid_teapot(1.0)


def generate_normal_lines(
    count: int = NORMAL_SAMPLE_COUNT,
    radius: float = NORMAL_RADIUS,
    length: float = NORMAL_LENGTH,
) -> list[tuple[Coordinates, Coordinates]]:
    """Generate radial normal vectors around a circle."""
    lines = []

    for i in range(count):
        angle = 2.0 * np.pi * i / count

        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        start = Coordinates(x, y, 0.0)
        normal = Coordinates(
            np.cos(angle),
            np.sin(angle),
            0.0,
        )

        lines.append(
            coordinate_pair_for_vector(
                start,
                normal,
                length,
            )
        )

    return lines

def draw_normals() -> None:
    """Draw normal vectors."""
    lines = generate_normal_lines()

    with gl_disabled(GLFixedFunctionCapability.LIGHTING):
        gl_color_rgb(RGBColor.GREEN)

        with gl_immediate_drawing(GLDrawMode.LINES):
            for start, end in lines:
                gl_vertex_line(start, end)


def draw_teapot_with_normals(wireframe_mode, show_normals):
    """Draw the teapot using built-in OpenGL primitives."""
    if wireframe_mode:
        with gl_disabled(GLFixedFunctionCapability.LIGHTING):
            with gl_polygon_mode_context(GLFillMode.LINE):
                gl_color_rgb(RGBColor.RED)
                glut_solid_teapot(1.0)
        return

    gl_color_rgb(RGBColor(0.8, 0.2, 0.2))
    glut_solid_teapot(1.0)

    if show_normals:
        draw_normals()
