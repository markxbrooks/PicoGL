from picogl.backend.gl.api.legacy.vertex import gl_vertex_any, gl_vertex_vec3
from picogl.backend.gl.api.vertex.normal_3f import gl_normal_vec3
from picogl.core.vec3 import Vec3
from picogl.examples.qt_legacy_molecular_viewer import Point3


def gl_legacy_draw_line(pos1: Point3, pos2: Point3) -> None:
    """Emit two vertices for a GL_LINES segment."""
    gl_vertex_any(pos1)
    gl_vertex_any(pos2)


def gl_legacy_draw_line_with_normal(vertex0: Vec3, vertex1: Vec3):
    """gl legacy draw line with normal"""
    gl_normal_vec3(vertex0.normalized())
    gl_vertex_vec3(vertex0)

    gl_normal_vec3(vertex1.normalized())
    gl_vertex_vec3(vertex1)
