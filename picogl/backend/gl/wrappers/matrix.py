from OpenGL.raw.GL.VERSION.GL_1_0 import glMatrixMode

from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode


def gl_matrix_mode(mode: GLLegacyMatrixMode):
    glMatrixMode(mode)