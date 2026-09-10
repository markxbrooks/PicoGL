from functools import wraps

from OpenGL.GL import glGetIntegerv
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_CURRENT_PROGRAM, glUseProgram
from OpenGL.raw.GL.VERSION.GL_3_0 import GL_VERTEX_ARRAY_BINDING

from picogl.backend.gl.api.vertex.vertex_array import gl_bind_vertex_array


def preserve_gl_state(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        prev_vao = glGetIntegerv(GL_VERTEX_ARRAY_BINDING)
        prev_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        try:
            return func(*args, **kwargs)
        finally:
            gl_bind_vertex_array(prev_vao)
            glUseProgram(prev_program)

    return wrapper
