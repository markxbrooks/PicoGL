"""
Provides a wrapper for configuring the viewing transformation using gluLookAt.

This module defines a utility function to set up the view transformation in a
3D space by specifying the position of the eye, the reference point the eye
is looking at, and the up vector. It serves as a direct interface to
OpenGL's gluLookAt function.
"""

from OpenGL.raw.GLU import gluLookAt, gluPerspective
from OpenGL.raw.GLUT import glutSolidTeapot, glutSwapBuffers


def glu_look_at(
    eye_x: float,
    eye_y: float,
    eye_z: float,
    center_x: float,
    center_y: float,
    center_z: float,
    up_x: float,
    up_y: float,
    up_z: float,
) -> None:
    """glu lookat"""
    gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, up_x, up_y, up_z)

def glu_perspective(fovy: float, aspect: float, near: float, far: float):
    """glu perspective"""
    gluPerspective(fovy, aspect, near, far)

def glut_swap_buffers():
    """glut swap buffers"""
    glutSwapBuffers()
    
def glut_solid_teapot(size):
    glutSolidTeapot(size)

