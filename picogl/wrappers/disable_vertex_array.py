"""
gl disable vertex array wrapper

"""

from OpenGL.GL import glDisableVertexAttribArray


def gl_disable_vertex_array(location: int):
    glDisableVertexAttribArray(location)
