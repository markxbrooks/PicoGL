"""
GL Polygon Mode
"""
from OpenGL.GL import GL_FILL, GL_FRONT_AND_BACK, glPolygonMode


def set_polygon_mode_fill() -> None:
    """Ensure secondary structure is always rendered as filled polygons"""
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
