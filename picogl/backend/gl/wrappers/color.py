"""
color
"""
from OpenGL.GL import glColorMaterial

from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.state.fill import GLColorMaterialMode


def gl_color_material(face: GLMaterialFace, mode: GLColorMaterialMode):
    glColorMaterial(face, mode)
