"""
gl disable vertex array wrapper

"""

from OpenGL.GL import glPolygonMode

from picogl.backend.capability import GLMaterialFace
from picogl.state.fill import GLFillMode


def gl_polygon_mode(face: GLMaterialFace = GLMaterialFace.FRONT, mode = GLFillMode.LINE):
    glPolygonMode(face, mode)
