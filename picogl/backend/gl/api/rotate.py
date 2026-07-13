"""
gl_rotate_f — thin wrapper around glRotatef(angle, x, y, z).
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glRotatef


def gl_rotate_f(angle: float, x: float, y: float, z: float) -> None:
    """Rotate by ``angle`` degrees about axis ``(x, y, z)``."""
    glRotatef(angle, x, y, z)
