from OpenGL.raw.GL.VERSION.GL_1_0 import glRotatef


def gl_rotate_f(angle, x, y, z) -> None:
    """gl rotate floats"""
    glRotatef(angle, x, y, z)
