"""
color
"""

from OpenGL.GL import glColorMaterial
from OpenGL.raw.GL.VERSION.GL_1_0 import glColor3f

from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.state.fill import GLColorMaterialMode


def gl_color_material(face: GLMaterialFace, mode: GLColorMaterialMode):
    glColorMaterial(face, mode)


def gl_color_3f(color) -> None:
    """gl color 3f"""
    glColor3f(*color)