"""
gl bind buffer wrapper

"""

from OpenGL.raw.GL.VERSION.GL_1_5 import glBindBuffer


def gl_bind_buffer(target, ebo_id: int | None):
    """gl bind buffer"""
    glBindBuffer(target, ebo_id)
