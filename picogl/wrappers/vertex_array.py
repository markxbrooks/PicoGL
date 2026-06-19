"""
gl bind buffer wrapper

"""
from OpenGL.raw.GL.VERSION.GL_3_0 import glBindVertexArray

def gl_bind_vertex_array(vao: int):
    """
    gl_bind_vertex_array

    :param vao: int
    """
    assert vao > 0
    glBindVertexArray(vao)