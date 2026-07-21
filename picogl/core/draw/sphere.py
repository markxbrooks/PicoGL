"""Legacy immediate-mode sphere rendering."""

from picogl.backend.gl.api.legacy.vertex import gl_vertex_vec3
from picogl.backend.gl.enums import GLDrawMode
from picogl.backend.gl.state.immediate import gl_immediate_drawing
from picogl.core.draw.line import (gl_legacy_draw_line,
                                   gl_legacy_draw_line_with_normal)
from picogl.core.vec3 import Vec3


def draw_latitude_ring_wireframe(ring: list[Vec3]) -> None:
    """Draw a latitude circle as a line loop."""
    with gl_immediate_drawing(GLDrawMode.LINE_LOOP):
        for vertex in ring:
            gl_vertex_vec3(vertex)


def draw_latitude_band_filled(ring0: list[Vec3], ring1: list[Vec3]) -> None:
    """Draw a filled band between two latitude rings as a triangle strip."""
    with gl_immediate_drawing(GLDrawMode.TRIANGLE_STRIP):
        for vertex0, vertex1 in zip(ring0, ring1):
            gl_legacy_draw_line_with_normal(vertex0, vertex1)


def draw_latitude_band_connectors(ring0: list[Vec3], ring1: list[Vec3]) -> None:
    """Draw meridian segments connecting two latitude rings."""
    with gl_immediate_drawing(GLDrawMode.LINES):
        for vertex0, vertex1 in zip(ring0, ring1):
            gl_legacy_draw_line(vertex0, vertex1)
