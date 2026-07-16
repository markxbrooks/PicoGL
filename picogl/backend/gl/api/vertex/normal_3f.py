"""Wrapper for glNormal3f."""

from OpenGL.raw.GL.VERSION.GL_1_0 import glNormal3f


def gl_normal_3f(x: float, y: float, z: float) -> None:
    """Set the current normal vector."""
    glNormal3f(x, y, z)
