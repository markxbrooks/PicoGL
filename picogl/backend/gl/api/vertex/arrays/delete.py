"""
delete Vertex arrays
"""

from OpenGL.GL import glDeleteVertexArrays


def gl_delete_vertex_arrays_old(handle):
    """glDeleteVertexArrays"""
    glDeleteVertexArrays(handle)
