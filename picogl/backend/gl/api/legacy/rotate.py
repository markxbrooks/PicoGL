"""
GL Rotate F
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glRotatef

from picogl.core.vec3 import Vec3


def gl_rotate_f(angle: float, x: float, y: float, z: float) -> None:
    """gl rotate floats"""
    glRotatef(angle, x, y, z)


def gl_rotate_vec3(angle: float, vec3: Vec3) -> None:
    """gl rotate floats"""
    gl_rotate_f(angle, vec3.x, vec3.y, vec3.z)
