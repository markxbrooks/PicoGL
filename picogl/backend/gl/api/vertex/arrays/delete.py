"""
delete Vertex arrays
"""


from OpenGL.GL import glDeleteVertexArrays

def gl_delete_vertex_arrays(handle):
    """glDeleteVertexArrays"""
    glDeleteVertexArrays(handle)
