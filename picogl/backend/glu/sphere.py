"""GLU quadric sphere helpers."""

from __future__ import annotations

from OpenGL.raw.GLU import gluDeleteQuadric, gluNewQuadric, gluSphere


def glu_new_quadric():
    """Create a new GLU quadric object."""
    return gluNewQuadric()


def glu_sphere(quadric, radius: float, slices: int, stacks: int) -> None:
    """Draw a sphere using a GLU quadric."""
    gluSphere(quadric, radius, slices, stacks)


def glu_delete_quadric(quadric) -> None:
    """Delete a GLU quadric object."""
    gluDeleteQuadric(quadric)


def glu_draw_sphere(radius: float = 0.3, slices: int = 12, stacks: int = 12) -> None:
    """Create a temporary quadric, draw a sphere, and delete the quadric."""
    quadric = glu_new_quadric()
    try:
        glu_sphere(quadric, radius, slices, stacks)
    finally:
        glu_delete_quadric(quadric)
