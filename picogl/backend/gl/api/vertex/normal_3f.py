"""
Wrappers for glNormal3f.
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glNormal3f
from picogl.core.vec3 import Vec3


def gl_normal_3f(x: float, y: float, z: float) -> None:
    """Set the current normal vector."""
    glNormal3f(x, y, z)


def gl_normal_vec3(vec3: Vec3) -> None:
    """Set the current normal vector from a Vector3 object"""
    gl_normal_3f(vec3.x, vec3.y, vec3.z)
