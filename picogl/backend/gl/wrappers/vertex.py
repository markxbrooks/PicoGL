"""
Wrapper for glVertex3f
"""
from OpenGL.raw.GL.VERSION.GL_1_0 import (
    glVertex3f,
)


def gl_vertex_3f(x: float, y: float, z: float) -> None:
    """vertex 3f"""
    glVertex3f(x, y, z)
