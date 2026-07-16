"""Wrapper for glFlush."""

from OpenGL.raw.GL.VERSION.GL_1_0 import glFlush


def gl_flush() -> None:
    """Flush the OpenGL command pipeline."""
    glFlush()
