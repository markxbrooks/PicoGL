from OpenGL.raw.GLU import gluPerspective


def glu_perspective(fovy: float, aspect: float, near: float, far: float):
    """glu perspective"""
    gluPerspective(fovy, aspect, near, far)
