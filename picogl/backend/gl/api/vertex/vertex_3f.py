"""
Wrapper for glVertex3f
"""

from molib.pdb.coordinate.coordinate import Coordinates
from OpenGL.raw.GL.VERSION.GL_1_0 import glVertex3f


def gl_vertex_3f(x: float, y: float, z: float) -> None:
    """vertex 3f"""
    glVertex3f(x, y, z)


def gl_vertex_coord(coord: Coordinates) -> None:
    """gl vertex coord"""
    gl_vertex_3f(coord.x, coord.y, coord.z)


def gl_vertex_line(coord_end: Coordinates, coord_start: Coordinates) -> None:
    """Emit a GL_LINES segment from start to end."""
    gl_vertex_coord(coord_start)
    gl_vertex_coord(coord_end)
