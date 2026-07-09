from typing import Any, Protocol, runtime_checkable

from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import gl_load_identity
from picogl.backend.gl.wrappers.color import gl_color_4f, gl_color_material
from picogl.backend.gl.wrappers.glu import glu_perspective
from picogl.backend.gl.wrappers.material import gl_material_f, gl_material_fv
from picogl.backend.gl.wrappers.matrix import gl_matrix_mode
from OpenGL.GL import glLightfv
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_MODELVIEW, GL_PROJECTION,
                                          GL_SHININESS, glTexCoord2f,
                                          glTranslatef, glVertex3f)
from picogl.backend.gl.capability import FACE_MAP
from picogl.backend.gl.state.fill import (GLColorMaterialMode, GLFace, GLLight,
                                          GLLightParameter)
from picogl.backend.gl.state.texture import TexCoord2f, Vertex3f
from picogl.backend.state import gl_value


@runtime_checkable
class LegacyPipelineProtocol(Protocol):
    """Fixed-function and immediate-mode pipeline operations (legacy gl only)."""

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
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)

    @staticmethod
    def set_matrix_mode_projection():
        gl_matrix_mode(GLLegacyMatrixMode.PROJECTION)

    @staticmethod
    def load_identity():
        gl_load_identity()

    @staticmethod
    def set_perspective(fovy, aspect, znear, zfar):
        glu_perspective(float(fovy), float(aspect), float(znear), float(zfar))

    @staticmethod
    def set_projection(fovy, aspect, znear, zfar):
        gl_matrix_mode(GL_PROJECTION)
        gl_load_identity()
        glu_perspective(float(fovy), float(aspect), float(znear), float(zfar))
        gl_matrix_mode(GL_MODELVIEW)

    @staticmethod
    def translate(x, y, z):
        glTranslatef(float(x), float(y), float(z))

    @staticmethod
    def set_light(position, light=GLLight.LIGHT0):
        glLightfv(gl_value(light), GLLightParameter.POSITION, position)

    @staticmethod
    def set_material(face, material):
        f = FACE_MAP.get(face, gl_value(face))
        gl_material_fv(f, GLLightParameter.AMBIENT, material.ambient)
        gl_material_fv(f, GLLightParameter.DIFFUSE, material.diffuse)
        gl_material_fv(f, GLLightParameter.SPECULAR, material.specular)
        gl_material_f(f, GL_SHININESS, material.shininess)

    @staticmethod
    def set_color_material(
        face: GLFace = GLFace.FRONT_AND_BACK,
        mode: GLColorMaterialMode = GLColorMaterialMode.AMBIENT_AND_DIFFUSE,
    ):
        f = FACE_MAP.get(face, gl_value(face))
        gl_color_material(f, gl_value(mode))

    @staticmethod
    def set_color(rgba: tuple[float, float, float, float]):
        gl_color_4f(rgba)

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
