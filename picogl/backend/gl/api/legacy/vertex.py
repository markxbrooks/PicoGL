from OpenGL import GL as gl
from OpenGL.raw.GL.VERSION.GL_1_0 import glVertex3f
from picogl.backend.gl.enums import GLNumeric


def gl_vertex_3f(v1):
    """gl vertex 3f"""
    glVertex3f(*v1)


def gl_vertex_pointer(size: int, type: GLNumeric, stride: int =0, pointer=None):
    """gl vertex pointer"""
    gl.glVertexPointer(size, type, stride, pointer)


def gl_color_pointer(size: int, type: GLNumeric, stride: int, pointer=None):
    """gl color pointer"""
    gl.glColorPointer(size, type, stride, pointer)
