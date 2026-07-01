from OpenGL.raw.GL.VERSION.GL_1_0 import glHint


def gl_hint(target, mode):
    glHint(target, mode)
