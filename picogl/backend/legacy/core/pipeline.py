from typing import Any, Protocol, runtime_checkable

from OpenGL.GL import glLightfv, glMaterialfv
from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_MODELVIEW,
    GL_PROJECTION,
    GL_SHININESS,
    glColor4f,
    glColorMaterial,
    glLoadIdentity,
    glMaterialf,
    glMatrixMode,
    glTexCoord2f,
    glTranslatef,
    glVertex3f,
)
from OpenGL.raw.GLU import gluPerspective

from picogl.backend.capability import FACE_MAP
from picogl.backend.state import gl_value
from picogl.state.fill import (
    GLColorMaterialMode,
    GLFace,
    GLLight,
    GLLightParameter,
)
from picogl.state.texture import TexCoord2f, Vertex3f


@runtime_checkable
class LegacyPipelineProtocol(Protocol):
    """Fixed-function and immediate-mode pipeline operations (legacy GL only)."""

    def set_matrix_mode_model_view(self): ...
    def set_matrix_mode_projection(self): ...
    def load_identity(self): ...
    def set_perspective(self, fovy, aspect, znear, zfar): ...
    def set_projection(self, fovy, aspect, znear, zfar): ...
    def translate(self, x, y, z): ...
    def set_light(self, position, light: Any = ...): ...
    def set_material(self, face, material): ...
    def set_color_material(
        self,
        face=...,
        mode=...,
    ): ...
    def set_color(self, rgba): ...
    def set_uniform_color(self, color, alpha): ...
    def tex_coord2f(self, coord: TexCoord2f): ...
    def vertex_3f(self, v1: Vertex3f): ...


class GLLegacyPipeline:
    """Fixed-function matrix, light, and material operations."""

    @staticmethod
    def set_matrix_mode_model_view():
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def set_matrix_mode_projection():
        glMatrixMode(GL_PROJECTION)

    @staticmethod
    def load_identity():
        glLoadIdentity()

    @staticmethod
    def set_perspective(fovy, aspect, znear, zfar):
        gluPerspective(float(fovy), float(aspect), float(znear), float(zfar))

    @staticmethod
    def set_projection(fovy, aspect, znear, zfar):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(float(fovy), float(aspect), float(znear), float(zfar))
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def translate(x, y, z):
        glTranslatef(float(x), float(y), float(z))

    @staticmethod
    def set_light(position, light=GLLight.LIGHT0):
        glLightfv(gl_value(light), GLLightParameter.POSITION, position)

    @staticmethod
    def set_material(face, material):
        f = FACE_MAP.get(face, gl_value(face))
        glMaterialfv(f, GLLightParameter.AMBIENT, material.ambient)
        glMaterialfv(f, GLLightParameter.DIFFUSE, material.diffuse)
        glMaterialfv(f, GLLightParameter.SPECULAR, material.specular)
        glMaterialf(f, GL_SHININESS, material.shininess)

    @staticmethod
    def set_color_material(
        face=GLFace.FRONT_AND_BACK,
        mode=GLColorMaterialMode.AMBIENT_AND_DIFFUSE,
    ):
        f = FACE_MAP.get(face, gl_value(face))
        glColorMaterial(f, gl_value(mode))

    @staticmethod
    def set_color(rgba):
        glColor4f(*rgba)

    def set_uniform_color(self, color, alpha):
        r, g, b = color[:3]
        self.set_color((r, g, b, 1.0 - alpha))

    @staticmethod
    def tex_coord2f(coord: TexCoord2f):
        return glTexCoord2f(coord.u, coord.v)

    @staticmethod
    def vertex_3f(v1: Vertex3f):
        glVertex3f(v1.x, v1.y, v1.z)


# Preferred public name for fixed-function pipeline access.
LegacyPipeline = GLLegacyPipeline
