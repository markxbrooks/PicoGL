from OpenGL.GL import glLightfv, glMaterialfv
from OpenGL.raw.GL.VERSION.GL_1_0 import glMatrixMode, GL_MODELVIEW, GL_PROJECTION, glLoadIdentity, glTranslatef, \
    GL_LIGHT0, GL_POSITION, GL_AMBIENT, GL_DIFFUSE, GL_SPECULAR, glMaterialf, GL_SHININESS, glColor4f, glTexCoord2f, \
    glVertex3f
from OpenGL.raw.GLU import gluPerspective

from picogl.backend.capability import FACE_MAP
from picogl.backend.state import gl_value
from picogl.state.texture import TexCoord2f, Vertex3f


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
    def set_light(position, light=GL_LIGHT0):
        glLightfv(gl_value(light), GL_POSITION, position)

    @staticmethod
    def set_material(face, material):
        f = FACE_MAP.get(face, gl_value(face))
        glMaterialfv(f, GL_AMBIENT, material.ambient)
        glMaterialfv(f, GL_DIFFUSE, material.diffuse)
        glMaterialfv(f, GL_SPECULAR, material.specular)
        glMaterialf(f, GL_SHININESS, material.shininess)

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
