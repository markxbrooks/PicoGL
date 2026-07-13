"""
gl_rotate_f
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glRotatef


def gl_rotate_f(x: float, y: float, z: float):
    """gl rotate f"""
    glRotatef(x, y, z)
