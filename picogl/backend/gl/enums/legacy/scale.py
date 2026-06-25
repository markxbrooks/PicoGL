"""
GL Push Matrix
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glScalef, glPushMatrix, glTranslatef, glRotatef, glPopMatrix, glLoadIdentity, \
    glViewport


def gl_viewport(x, y, width, height):
    glViewport(x, y, width, height)


def gl_load_identity():
    glLoadIdentity()


def gl_pop_matrix():
    glPopMatrix()


def gl_push_matrix():
    glPushMatrix()


def gl_translatef(x: float, y: float, zoom: float):
    glTranslatef(x, y, float(zoom))


def gl_scalef(x: float, y: float, z: float):
    glScalef(x, y, z)


def gl_rotatef(angle, x: float, y: float, z: float):
    glRotatef(float(angle), x, y, z)
