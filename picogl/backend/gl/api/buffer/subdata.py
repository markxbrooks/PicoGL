from OpenGL.GL import glBufferSubData


def gl_buffer_subdata(target, offset, size, data):
    """
    gl buffer subdata
    """
    glBufferSubData(target, offset, size, data)