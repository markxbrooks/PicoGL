from typing import Sequence

from molib.pdb.coordinate.coordinate import Coordinates
from picogl.backend.gl.api.legacy.vertex import gl_vertex_vec3
from picogl.backend.gl.api.vertex.normal_3f import gl_normal_vec3
from picogl.backend.gl.api.vertex.vertex_3f import gl_vertex_line
from picogl.core.vec3 import Vec3

Point3 = Vec3 | Sequence[float]


def _point_to_coordinates(point: Point3) -> Coordinates:
    if isinstance(point, Vec3):
        return Coordinates(point.x, point.y, point.z)
    return Coordinates.from_array(point)


def gl_legacy_draw_line(pos1: Point3, pos2: Point3) -> None:
    """Emit two vertices for a GL_LINES segment."""
    gl_vertex_line(_point_to_coordinates(pos2), _point_to_coordinates(pos1))


def gl_legacy_draw_line_with_normal(vertex0: Vec3, vertex1: Vec3):
    """gl legacy draw line with normal"""
    gl_normal_vec3(vertex0.normalized())
    gl_vertex_vec3(vertex0)

    gl_normal_vec3(vertex1.normalized())
    gl_vertex_vec3(vertex1)
