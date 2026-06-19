"""
gl bind buffer wrapper

"""

from OpenGL.raw.GL.VERSION.GL_3_0 import glBindVertexArray


def gl_bind_vertex_array(vao: int):
    """
    gl_bind_vertex_array

    :param vao: int VAO handle; ``0`` unbinds the current VAO.
    """
    assert vao is not None and vao >= 0
    glBindVertexArray(vao)
