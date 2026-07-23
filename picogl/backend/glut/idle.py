from OpenGL.GLUT import glutIdleFunc


def glut_idle_func(func):
    glutIdleFunc(func)