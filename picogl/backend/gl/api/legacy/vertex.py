"""
Vertex functions
"""

from typing import Sequence

from OpenGL import GL as gl
from OpenGL.raw.GL.VERSION.GL_1_0 import glVertex3f
from picogl.backend.gl.enums import GLNumeric
from picogl.core.vec3 import Vec3


def gl_vertex_3f(x, y, z) -> None:
    """gl vertex 3f"""
    glVertex3f(x, y, z)


def gl_vertex_tuple_3f(v1) -> None:
    """gl vertex 3f"""
    gl_vertex_3f(*v1)


def gl_vertex_vec3(vec3: Vec3) -> None:
    """gl vertex vec3"""
    gl_vertex_3f(vec3.x, vec3.y, vec3.z)


def gl_vertex_any(pos1: Vec3 | Sequence[float]):
    """gl vertex any"""
    if isinstance(pos1, Vec3):
        gl_vertex_vec3(pos1)
    else:
        gl_vertex_tuple_3f((pos1[0], pos1[1], pos1[2]))


def gl_vertex_pointer(size: int, type: GLNumeric, stride: int = 0, pointer=None):
    """gl vertex pointer"""
    gl.glVertexPointer(size, type, stride, pointer)


def gl_color_pointer(size: int, type: GLNumeric, stride: int, pointer=None):
    """gl color pointer"""
    gl.glColorPointer(size, type, stride, pointer)
