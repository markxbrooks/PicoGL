from OpenGL.raw.GLUT import glutSolidTeapot, glutWireTeapot


def glut_solid_teapot(size: float) -> None:
    """Draw a solid teapot of the given size."""
    glutSolidTeapot(size)


def glut_wire_teapot(size: float) -> None:
    """Draw a wireframe teapot of the given size."""
    glutWireTeapot(size)
